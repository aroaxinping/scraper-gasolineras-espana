import folium
from folium.plugins import MarkerCluster
import pandas as pd
import os

MAP_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mapa_precios.html")

def get_color(price, p25, p75):
    if pd.isna(price):
        return "gray"
    if price <= p25:
        return "green"
    elif price >= p75:
        return "red"
    return "orange"

def generate_map(df: pd.DataFrame):
    """Genera un mapa interactivo con folium."""
    print("Generando mapa de precios...")
    
    # Filtrar estaciones con coordenadas válidas
    df_map = df.dropna(subset=["latitud", "longitud"])
    
    if df_map.empty:
        print("No hay datos de coordenadas para generar el mapa.")
        return

    # Usamos Gasolina 95 para la escala de colores (por defecto)
    p25 = df_map["gasolina95"].quantile(0.25)
    p75 = df_map["gasolina95"].quantile(0.75)

    # Crear mapa con tiles de CartoDB (más elegantes y sin errores 403)
    m = folium.Map(
        location=[40.4167, -3.70325], 
        zoom_start=6,
        tiles='Cartodb Positron',
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
    )
    
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in df_map.iterrows():
        color = get_color(row["gasolina95"], p25, p75)
        
        # Popup estilo interactivo con HTML/CSS
        popup_html = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; min-width: 200px;">
            <div style="background-color: {color}; color: white; padding: 10px; border-radius: 5px 5px 0 0; text-align: center;">
                <b style="font-size: 16px;">{row['estacion']}</b>
            </div>
            <div style="padding: 10px; border: 1px solid #ddd; border-radius: 0 0 5px 5px; background: white;">
                <p style="margin: 5px 0; color: #666; font-size: 12px;">📍 {row['direccion']}</p>
                <hr style="border: 0; border-top: 1px solid #eee;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 5px 0; font-weight: bold; color: #333;">Gasolina 95</td>
                        <td style="padding: 5px 0; text-align: right; color: #2ecc71; font-weight: bold;">{row['gasolina95'] if not pd.isna(row['gasolina95']) else '--'} €/L</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px 0; font-weight: bold; color: #333;">Diesel A</td>
                        <td style="padding: 5px 0; text-align: right; color: #3498db; font-weight: bold;">{row['diesel'] if not pd.isna(row['diesel']) else '--'} €/L</td>
                    </tr>
                </table>
            </div>
        </div>
        """
        
        folium.CircleMarker(
            location=[row["latitud"], row["longitud"]],
            radius=7,
            popup=folium.Popup(popup_html, max_width=300),
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            weight=1
        ).add_to(marker_cluster)

    # Añadir leyenda opcional si se desea en el futuro aquí.
    m.save(MAP_PATH)
    print(f"✅ Mapa generado satisfactoriamente: {MAP_PATH}")

