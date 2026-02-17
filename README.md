# Scraper Gasolineras España v2.0 🚀

[![Scrape](https://github.com/aroaxinping/scraper-gasolineras-espana/actions/workflows/scrape.yml/badge.svg)](https://github.com/aroaxinping/scraper-gasolineras-espana/actions/workflows/scrape.yml)

Monitor de precios de carburantes en España con histórico persistente, mapas interactivos y alertas automáticas.

Consulta las novedades de la versión 2.0 en el [CHANGELOG.md](./CHANGELOG.md).

## 🛠️ Instalación y Uso

```bash
pip install -r requirements.txt
python -m src.scraper
```

#### Solución rápida (Si la API falla)
1. Abre [este enlace](https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/) en tu navegador.
2. Tienes dos opciones:
   - **Opción A (Manual)**: Selecciona todo el código JSON, pégalo en `data/fichero_api.json` y corre el script.
   - **Opción B (Automática - RECOMENDADA)**: Si el JSON es muy grande o te lías, selecciona **TODO** el contenido de la página (Ctrl+A), pégalo en `data/entrada_bruta.txt` y ejecuta:
     ```bash
     python -m src.tools.import_raw
     ```
     Luego ya puedes ejecutar el script normal `python -m src.scraper`. lo procesará automáticamente.

## 📁 Estructura del Proyecto
- `data/`: CSVs semanales, Base de Datos SQLite y backups.
- `src/scraper.py`: Motor principal (Descarga, DB, Alertas y Mapas).
- `src/analyze.py`: Herramientas de análisis histórico.
- `src/utils.py`: Normalización de datos.
- `mapa_precios.html`: Mapa interactivo generado.

## ⚖️ Fuente de datos
API REST pública del Ministerio de Industria y Energía. No requiere API Key.
