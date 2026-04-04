import pandas as pd
from datetime import date
from src.scraper import parse_stations
from src.database import save_to_sqlite
from src.map_generator import generate_map

# Mock data based on the structure of the API
mock_data = {
    "ListaEESSPrecio": [
        {
            "Provincia": "MADRID",
            "Municipio": "Madrid",
            "Rótulo": "REPSOL",
            "Dirección": "CALLE ALCALA, 100",
            "Precio Gasolina 95 E5": "1,659",
            "Precio Gasoleo A": "1,559",
            "Latitud": "40,4167",
            "Longitud (WGS84)": "-3,7032"
        },
        {
            "Provincia": "BARCELONA",
            "Municipio": "Barcelona",
            "Rótulo": "CEPSA",
            "Dirección": "AV DIAGONAL, 200",
            "Precio Gasolina 95 E5": "1,759",
            "Precio Gasoleo A": "1,659",
            "Latitud": "41,3851",
            "Longitud (WGS84)": "2,1734"
        },
        {
            "Provincia": "VALENCIA / VALÈNCIA",
            "Municipio": "Valencia",
            "Rótulo": "GALP",
            "Dirección": "PLAZA AYUNTAMIENTO, 1",
            "Precio Gasolina 95 E5": "1,559",
            "Precio Gasoleo A": "1,459",
            "Latitud": "39,4699",
            "Longitud (WGS84)": "-0,3763"
        }
    ]
}

def run_mock_test():
    print("Ejecutando prueba con datos ficticios...")
    df = parse_stations(mock_data)
    
    # Probar normalización
    print("\nProvincias normalizadas pulsadas:")
    print(df[["provincia", "municipio"]])

    # Probar base de datos
    save_to_sqlite(df)
    
    # Probar mapa
    generate_map(df)
    
    print("\nPrueba completada con éxito.")

if __name__ == "__main__":
    run_mock_test()
