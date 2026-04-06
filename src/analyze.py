"""
Analisis rapido de precios de gasolineras.
Compara el CSV mas reciente con el anterior (si existe).
"""

import os
import sys
from glob import glob

import sqlite3
import pandas as pd
from src.database import DB_PATH

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def get_csv_files() -> list[str]:
    """Devuelve CSVs de precios ordenados por fecha (mas reciente primero)."""
    files = sorted(glob(os.path.join(DATA_DIR, "precios_*.csv")), reverse=True)
    return files


def mean_by_province(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Media de precio por provincia, ordenada de mas barata a mas cara."""
    return (
        df.groupby("provincia")[col]
        .mean()
        .dropna()
        .sort_values()
        .reset_index()
        .rename(columns={col: f"media_{col}"})
    )


def analyze_trends_sqlite():
    """Análisis de tendencias usando la base de datos SQLite."""
    if not os.path.exists(DB_PATH):
        print("Base de datos no encontrada. Ejecuta scraper.py primero.")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        print("\n--- Análisis de Tendencias (SQLite) ---")
        # Media nacional por fecha
        query = """
        SELECT fecha, AVG(gasolina95) as avg_95, AVG(diesel) as avg_diesel 
        FROM precios_historicos 
        GROUP BY fecha 
        ORDER BY fecha ASC
        """
        df_trends = pd.read_sql(query, conn)
        print(df_trends.to_string(index=False))

        # Gasolinera más barata en los últimos 6 meses (ejemplo de consulta compleja)
        print("\nTop 3 gasolineras más baratas históricamente (Gasolina 95):")
        query_cheap = """
        SELECT estacion, municipio, provincia, gasolina95, fecha 
        FROM precios_historicos 
        WHERE gasolina95 IS NOT NULL
        ORDER BY gasolina95 ASC 
        LIMIT 3
        """
        df_cheap = pd.read_sql(query_cheap, conn)
        print(df_cheap.to_string(index=False))
    finally:
        conn.close()


def main():
    # Análisis tradicional basado en CSV
    files = get_csv_files()
    if files:
        latest = pd.read_csv(files[0])
        print(f"Último archivo: {os.path.basename(files[0])}")
        
        # Comparación con semana anterior
        if len(files) >= 2:
            previous = pd.read_csv(files[1])
            print(f"\nCambio vs semana anterior ({os.path.basename(files[1])}):")
            for col in ["gasolina95", "diesel"]:
                curr_mean = latest[col].mean()
                prev_mean = previous[col].mean()
                diff = curr_mean - prev_mean
                pct = (diff / prev_mean) * 100 if prev_mean else 0
                direction = "subió" if diff > 0 else "bajó"
                print(f"  {col}: {prev_mean:.3f} -> {curr_mean:.3f} ({direction} {abs(pct):.2f}%)")

    # Nuevo análisis basado en SQLite
    analyze_trends_sqlite()


if __name__ == "__main__":
    main()
