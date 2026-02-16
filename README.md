# Scraper Gasolineras Espana

[![Scrape](https://github.com/aroaxinping/scraper-gasolineras-espana/actions/workflows/scrape.yml/badge.svg)](https://github.com/aroaxinping/scraper-gasolineras-espana/actions/workflows/scrape.yml)

Scraper automatizado que recoge precios de gasolineras en Espana cada semana desde la API publica de MINETUR (Ministerio de Industria).

Los datos se guardan en `data/precios_YYYY-MM-DD.csv` y se actualizan automaticamente cada lunes a las 8:00 UTC via GitHub Actions.

## Uso manual

```bash
pip install -r requirements.txt
python src/scraper.py
python src/analyze.py
```

## Fuente de datos

API REST publica del Ministerio de Industria (MINETUR/CNMC):
https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/

No requiere API key.

## Estructura

```
data/              <- CSVs con precios semanales
src/scraper.py     <- descarga y parsea datos de la API
src/analyze.py     <- estadisticas resumen
.github/workflows/ <- automatizacion semanal
```
