import re
import json
import os
import sys

def parse_raw_text(text):
    """
    Intenta parsear el 'chorizo' de texto copiado del navegador.
    El formato es extremadamente compacto y contiene etiquetas XML/Excel pegadas.
    """
    stations = []
    
    # Extraer fecha (generalmente al principio: DD/MM/AAAA HH:MM:SS)
    date_match = re.search(r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})', text)
    fecha_proceso = date_match.group(1) if date_match else "04/04/2026 20:45:22"

    # Primero eliminamos TODAS las etiquetas XML/Excel pegadas para que no confundan al regex
    # Ejemplo: <_x0025__x0020_BioEtanol>0,0
    clean_text = re.sub(r'<.*?>', '', text)
    
    # También limpiamos los precios basura que vienen en los tags de éster metílico
    # que suelen tener el formato 0,0XXXXX... y se confunden con precios reales
    # Este paso es redundante por el re.sub de arriba pero asegura la limpieza.

    
    # El patrón principal busca:
    # 1. Dirección (texto hasta L-[D/S])
    # 2. Horario (L-D: ...)
    # 3. Latitud (Número con coma)
    # 4. Municipio (Mayúsculas)
    # 5. Longitud (Número con coma, puede ser negativo)
    # 6. Nombre/Rótulo + Precios (Mezclados)
    # 7. Provincia (Mayúsculas después de precios)
    
    # Patrón experimental ajustado al texto del usuario
    # Explicación:
    # (?P<dir>.*?) -> Dirección
    # (?P<horario>L-[D-S]: [\d:-]+(?:; [D-S]: [\d:-]+)?) -> Horario
    # (?P<lat>\d{2},\d{6}) -> Latitud
    # (?P<mun>[A-ZÁÉÍÓÚÑ \-/()']+) -> Municipio
    # (?P<lon>-?\d,\d{6}) -> Longitud
    # (?P<nombre_precios>.*?) -> Bloque con nombre y precios
    # (?P<prov>ALBACETE|ALICANTE|VALENCIA|CASTELLON|MADRID|...) -> Provincia (añadiremos las comunes)
    
    # Lista completa de provincias de España (mayúsculas y algunas versiones bilingües)
    PROVINCIAS = (
        "ALAVA|ALBACETE|ALICANTE|ALICANTE/ALACANT|ALMERIA|ASTURIAS|AVILA|BADAJOZ|BARCELONA|BIZKAIA|BURGOS|CACERES|CADIZ|CANTABRIA|CASTELLON|CASTELLON/CASTELLO|"
        "CEUTA|CIUDAD REAL|CORDOBA|CUENCA|GIPUZKOA|GIRONA|GRANADA|GUADALAJARA|HUELVA|HUESCA|ILLES BALEARS|JAEN|LA RIOJA|LAS PALMAS|LEON|LLEIDA|LUGO|MADRID|"
        "MALAGA|MELILLA|MURCIA|NAVARRA|OURENSE|PALENCIA|PONTEVEDRA|SALAMANCA|SANTA CRUZ DE TENERIFE|SEGOVIA|SEVILLA|SORIA|TARRAGONA|TERUEL|TOLEDO|VALENCIA|VALLADOLID|ZAMORA|ZARAGOZA"
    )

    pattern = r'(?P<dir>.+?)(?P<horario>L-[D-S]: (?:24H|[\d:-]+)(?:; [D-S]: [\d:-]*)?)(?P<lat>[3-4]\d,\d{6})(?P<mun>.+?)(?P<lon>-?\d,\d{6})(?P<data_mix>.+?)(?P<prov>' + PROVINCIAS + ')'


    for match in re.finditer(pattern, clean_text):
        d = match.groupdict()
        
        # Extraer precios del data_mix (generalmente al final del bloque antes de la provincia)
        # Los precios tienen formato X,XXX
        prices = re.findall(r'(\d,\d{3})', d['data_mix'])
        
        # Filtro de precios absurdos (0.015, etc.)
        # Solo guardamos el precio si es >= 0.50
        def safe_price(p_str):
            try:
                val = float(p_str.replace(',', '.'))
                return p_str if val >= 0.50 else ""
            except:
                return ""

        price95 = safe_price(prices[0]) if len(prices) > 0 else ""
        priceDiesel = safe_price(prices[1]) if len(prices) > 1 else (safe_price(prices[0]) if len(prices) == 1 else "")
        pricePremium = safe_price(prices[2]) if len(prices) > 2 else ""

        # Limpiar el nombre (quitar basura xml pegada)
        raw_name = d['data_mix']
        for p in prices:
            raw_name = raw_name.replace(p, '')
        
        clean_name = re.sub(r'^[DIRdmPN]+', '', raw_name).strip()
        
        # Limpiar municipio (a veces arrastra un guion al final)
        clean_mun = d['mun'].strip().rstrip('-').strip()

        station = {
            "Provincia": d['prov'],
            "Municipio": clean_mun,
            "Dirección": d['dir'].strip(),
            "Rótulo": clean_name if clean_name else "DESCONOCIDO",
            "Precio Gasolina 95 E5": price95,
            "Precio Gasoleo A": priceDiesel,
            "Precio Gasoleo Premium": pricePremium,
            "Latitud": d['lat'],
            "Longitud (WGS84)": d['lon']
        }
        stations.append(station)

        
    return {
        "Fecha": fecha_proceso,
        "ListaEESSPrecio": stations
    }

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    input_path = os.path.join(base_dir, "data", "entrada_bruta.txt")
    output_path = os.path.join(base_dir, "data", "fichero_api.json")
    
    if not os.path.exists(input_path):
        print(f"❌ Error: No se encuentra el archivo {input_path}")
        print("Crea el archivo y pega el texto de la web allí.")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        print("⚠️ El archivo de entrada está vacío.")
        return

    print("🛠️ Procesando texto bruto...")
    data = parse_raw_text(content)
    
    count = len(data["ListaEESSPrecio"])
    if count == 0:
        print("❌ No se ha podido extraer ninguna gasolinera. Comprueba el formato del texto.")
        return

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"✅ ¡Éxito! Se han extraído {count} gasolineras.")
    print(f"📂 Archivo generado: {output_path}")
    print("\nAhora puedes ejecutar: python -m src.scraper")

if __name__ == "__main__":
    main()
