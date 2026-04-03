"""
Scraper de precios de gasolineras en Espana.
Fuente: API publica MINETUR (Ministerio de Industria).
"""

import os
import sys
import time
from datetime import date

import pandas as pd
import requests

API_URL = (
    "https://sedeaplicaciones.minetur.gob.es"
    "/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"
)

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 10

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def fetch_data() -> dict:
    """Descarga datos de la API con reintentos."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Intento {attempt}/{MAX_RETRIES}...")
            resp = requests.get(API_URL, timeout=60)
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError) as e:
            print(f"Error en intento {attempt}: {e}")
            if attempt < MAX_RETRIES:
                print(f"Reintentando en {RETRY_DELAY_SECONDS}s...")
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                print("Todos los intentos fallaron.")
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
        records.append({
            "provincia": s.get("Provincia", "").strip(),
            "municipio": s.get("Municipio", "").strip(),
            "estacion": s.get("Rótulo", "").strip(),
            "direccion": s.get("Dirección", "").strip(),
            "gasolina95": parse_price(s.get("Precio Gasolina 95 E5", "")),
            "diesel": parse_price(s.get("Precio Gasoleo A", "")),
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
    print("Descargando precios de gasolineras...")
    data = fetch_data()
    df = parse_stations(data)
    save_csv(df)
    print_summary(df)
    print("\nScraping completado.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
