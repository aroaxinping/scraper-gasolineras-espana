"""
Scraper de precios de gasolineras en Espana.
Fuente: API publica MINETUR (Ministerio de Industria).
"""

import os
import sys
import time
import json
from datetime import date

import pandas as pd
import requests

from src.utils import normalize_province, normalize_string
from src.database import save_to_sqlite, get_last_average_prices
from src.map_generator import generate_map
from src.alerts import check_for_drops

API_URL = (
    "https://sedeaplicaciones.minetur.gob.es"
    "/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"
)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
DATA_DIR = "data"

MAX_RETRIES = 5
INITIAL_RETRY_DELAY = 10


def fetch_data() -> dict:
    """Descarga datos de la API usando una sesión y cabeceras de navegador real."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://sedeaplicaciones.minetur.gob.es/PreciosCarburantes/",
        "Origin": "https://sedeaplicaciones.minetur.gob.es",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "DNT": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    
    # Usar sesión para mantener la conexión y manejar cookies automáticamente
    with requests.Session() as session:
        session.headers.update(headers)
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # Pequeño delay antes del primer intento para no ser "explosivos"
                if attempt == 1:
                    time.sleep(1)
                    
                print(f"Intento {attempt}/{MAX_RETRIES} (vía Session)...")
                
                # Deshabilitamos la verificación SSL solo como último recurso 
                # (algunos servidores del gobierno tienen cadenas de certificados rotas)
                resp = session.get(API_URL, timeout=90)
                resp.raise_for_status()
                
                return resp.json()
                
            except (requests.RequestException, ValueError) as e:
                delay = INITIAL_RETRY_DELAY * (2 ** (attempt - 1))
                print(f"Error en intento {attempt}: {e}")
                
                # Si es un ConnectionReset (10054), intentamos esperar un poco más
                if "10054" in str(e):
                    print("⚠️ El servidor cortó la conexión. Aumentando espera...")
                    delay += 10
                
                if attempt < MAX_RETRIES:
                    print(f"Reintentando en {delay}s...")
                    time.sleep(delay)
                else:
                    print("Se agotaron los reintentos.")
                    raise


def parse_price(value: str) -> float | None:
    """Convierte precio string (con coma decimal) a float."""
    if not value or value.strip() == "":
        return None
    try:
        return float(value.replace(",", "."))
    except ValueError:
        return None


def parse_stations(data: dict) -> pd.DataFrame:
    """Extrae campos relevantes de la respuesta de la API."""
    stations = data.get("ListaEESSPrecio", [])
    if not stations:
        raise ValueError("No se encontraron estaciones en la respuesta.")

    records = []
    for s in stations:
        g95 = parse_price(s.get("Precio Gasolina 95 E5", ""))
        die = parse_price(s.get("Precio Gasoleo A", ""))
        
        # Filtro de Outliers (0.50 - 3.50 €)
        if g95 and (g95 < 0.5 or g95 > 3.5): g95 = None
        if die and (die < 0.5 or die > 3.5): die = None

        records.append({
            "provincia": normalize_province(s.get("Provincia", "")),
            "municipio": normalize_string(s.get("Municipio", "")),
            "estacion": s.get("Rótulo", "").strip(),
            "direccion": s.get("Dirección", "").strip(),
            "gasolina95": g95,
            "diesel": die,
            "latitud": parse_price(s.get("Latitud", "")),
            "longitud": parse_price(s.get("Longitud (WGS84)", "")),
            "fecha": date.today().isoformat(),
        })


    df = pd.DataFrame(records)
    print(f"Estaciones parseadas: {len(df)}")
    return df


def save_csv(df: pd.DataFrame) -> str:
    """Guarda el DataFrame como CSV en data/."""
    os.makedirs(DATA_DIR, exist_ok=True)
    filename = f"precios_{date.today().isoformat()}.csv"
    filepath = os.path.join(DATA_DIR, filename)
    df.to_csv(filepath, index=False)
    print(f"Guardado: {filepath}")
    return filepath


def print_summary(df: pd.DataFrame) -> None:
    """Imprime estadisticas resumen tras el scraping."""
    print("\n--- Resumen ---")
    print(f"Total estaciones: {len(df)}")

    g95 = df["gasolina95"].dropna()
    diesel = df["diesel"].dropna()

    if not g95.empty:
        print(f"Gasolina 95 - media: {g95.mean():.3f} EUR/L, "
              f"min: {g95.min():.3f}, max: {g95.max():.3f}")
    if not diesel.empty:
        print(f"Diesel      - media: {diesel.mean():.3f} EUR/L, "
              f"min: {diesel.min():.3f}, max: {diesel.max():.3f}")

    print(f"Provincias cubiertas: {df['provincia'].nunique()}")


def main():
    print("🚀 Iniciando scraper de gasolineras v2.0")
    print("💡 Nota: Si la API falla, puedes descargar los datos manualmente y")
    print("   guardarlos en 'data/fichero_api.json' para saltarte la espera.")
    print("-" * 50)
    data = None
    
    # 1. Comprobación inicial de archivo local
    fallback_path = os.path.join(DATA_DIR, "fichero_api.json")
    if os.path.exists(fallback_path):
        print(f"📦 Se ha detectado un archivo local: {fallback_path}")
        confirm = input("¿Quieres usar los datos de este archivo en lugar de descargar de la API? (s/n): ").lower()
        if confirm == 's':
            with open(fallback_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    print("✅ Cargando datos desde el archivo local...")
                except json.JSONDecodeError:
                    print("❌ Error: El archivo local no tiene un formato JSON válido. Intentando vía API...")

    # 2. Si no hay datos (o el usuario eligió no usar el local), intentar vía API
    if not data:
        try:
            data = fetch_data()
        except Exception as e:
            print(f"\n❌ Error crítico al conectar con la API: {e}")
            print("-" * 50)
            print("💡 SOLUCIÓN RÁPIDA (PLAN B):")
            print("1. Abre esta URL: https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/")
            print("2. Copia todo el contenido y guárdalo en: data/fichero_api.json")
            print("-" * 50)
            print("💡 SOLUCIÓN AUTOMÁTICA (PLAN C - Recomendada):")
            print("1. Si entrar en la URL anterior es un lío, selecciona TODO el texto de la web (aunque sea la tabla visual).")
            print("2. Pégalo en el archivo: data/entrada_bruta.txt")
            print("3. Ejecuta: python -m src.tools.import_raw")
            print("4. Vuelve a ejecutar este script.")
            print("-" * 50)
            sys.exit(1)

    # 3. Procesamiento normal de los datos (vengan de donde vengan)
    df = parse_stations(data)
    
    # Alertas: comparar antes de guardar la nueva data
    previous_means = get_last_average_prices()
    current_means = {
        "g95": df["gasolina95"].mean(),
        "diesel": df["diesel"].mean()
    }
    check_for_drops(current_means, previous_means)

    # Persistencia
    save_csv(df)
    save_to_sqlite(df)
    
    # Visualización
    generate_map(df)
    
    print_summary(df)
    print("\n✅ ¡Proceso completado con éxito!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
