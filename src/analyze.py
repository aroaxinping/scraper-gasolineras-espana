"""
Analisis rapido de precios de gasolineras.
Compara el CSV mas reciente con el anterior (si existe).
"""

import os
import sys
from glob import glob

import pandas as pd

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


def compare_weeks(current: pd.DataFrame, previous: pd.DataFrame) -> None:
    """Compara medias entre semana actual y anterior."""
    for col in ["gasolina95", "diesel"]:
        curr_mean = current[col].mean()
        prev_mean = previous[col].mean()
        diff = curr_mean - prev_mean
        pct = (diff / prev_mean) * 100 if prev_mean else 0
        direction = "subio" if diff > 0 else "bajo"
        print(f"  {col}: {prev_mean:.3f} -> {curr_mean:.3f} "
              f"({direction} {abs(pct):.2f}%)")


def main():
    files = get_csv_files()
    if not files:
        print("No hay CSVs en data/. Ejecuta primero scraper.py.")
        sys.exit(1)

    print(f"Archivos encontrados: {len(files)}")
    latest = pd.read_csv(files[0])
    print(f"\nUltimo archivo: {os.path.basename(files[0])}")
    print(f"Estaciones: {len(latest)}")

    # Top 5 provincias mas baratas y mas caras
    for col, label in [("gasolina95", "Gasolina 95"), ("diesel", "Diesel")]:
        ranking = mean_by_province(latest, col)
        print(f"\n--- {label} por provincia ---")
        print("Mas baratas:")
        for _, row in ranking.head(5).iterrows():
            print(f"  {row['provincia']}: {row[f'media_{col}']:.3f} EUR/L")
        print("Mas caras:")
        for _, row in ranking.tail(5).iterrows():
            print(f"  {row['provincia']}: {row[f'media_{col}']:.3f} EUR/L")

    # Comparacion con semana anterior
    if len(files) >= 2:
        previous = pd.read_csv(files[1])
        print(f"\nCambio vs semana anterior ({os.path.basename(files[1])}):")
        compare_weeks(latest, previous)
    else:
        print("\nSolo hay un archivo, no se puede comparar con semana anterior.")


if __name__ == "__main__":
    main()
