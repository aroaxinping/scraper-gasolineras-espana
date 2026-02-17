import sqlite3
import os
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "precios_historicos.db")

def save_to_sqlite(df: pd.DataFrame):
    """Guarda el DataFrame en la base de datos SQLite."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        # Añadimos a la tabla. Si no existe, pandas la crea.
        df.to_sql("precios_historicos", conn, if_exists="append", index=False)
        print(f"Base de datos actualizada: {DB_PATH}")
    finally:
        conn.close()

def get_last_average_prices() -> dict:
    """Obtiene los precios medios de la última fecha registrada en la DB."""
    if not os.path.exists(DB_PATH):
        return {}
        
    conn = sqlite3.connect(DB_PATH)
    try:
        # Primero buscamos la última fecha disponible
        query_date = "SELECT MAX(fecha) FROM precios_historicos"
        last_date = pd.read_sql(query_date, conn).iloc[0,0]
        
        if not last_date:
            return {}
            
        # Calculamos medias para esa fecha
        query_means = f"SELECT AVG(gasolina95) as g95, AVG(diesel) as diesel FROM precios_historicos WHERE fecha = '{last_date}'"
        means = pd.read_sql(query_means, conn).iloc[0].to_dict()
        return means
    finally:
        conn.close()
