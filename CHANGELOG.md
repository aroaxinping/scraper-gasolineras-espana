# Historial de Cambios (Changelog)

Todos los cambios notables en este proyecto se documentarán en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
y este proyecto se rige por el [Versionado Semántico](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-04-04

### Añadido
- **Interfaz de Mapa Premium**: Popups del mapa mejorados con tablas HTML/CSS profesionales, colores según el precio y mejor tipografía.
- **Importador de Datos Brutos**: Nueva utilidad `src/tools/import_raw.py` para procesar automáticamente texto "sucio" copiado directamente de las tablas del navegador.
- **Limpieza de Datos Agresiva**: Implementada limpieza de etiquetas y validación de precios en el importador para asegurar la alta calidad de los datos.

### Cambiado
- **Proveedor de Mapas**: Cambio de OpenStreetMap a **CartoDB Positron** para resolver errores 403 (Acceso Bloqueado) y ofrecer una estética más limpia.
- **Filtro de Valores Atípicos**: Integrado un filtro de seguridad (rango 0.50€ - 3.50€) para ignorar entradas de precios erróneas en los datos de origen.

### Corregido
- **Desplazamiento de Coordenadas**: Resuelto un error crítico donde las longitudes negativas se procesaban mal, haciendo que las estaciones aparecieran en África.
- **Procesamiento de Horarios**: Actualizado el Regex para soportar la notación `24H` en estaciones de servicio permanentes.

## [2.0.0] - 2026-04-04

### Añadido
- **Almacenamiento Persistente**: Migración del seguimiento de precios históricos a una base de datos SQLite (`data/precios_historicos.db`).
- **Visualización Interactiva**: Generación automática de mapas usando Folium (`mapa_precios.html`) con códigos de color basados en el precio.
- **Alertas Inteligentes**: Lógica para detectar bajadas de precio significativas (>2%) comparadas con los promedios históricos previos.
- **Normalización de Datos**: Módulo para estandarizar nombres de provincias y municipios, resolviendo inconsistencias en los datos de la API.
- **Carga Manual (Fallback)**: Soporte para cargar datos JSON desde un archivo local (`data/fichero_api.json`) si la API del gobierno no responde.

### Cambiado
- **Robustez del Scraper**: Refactorización de `fetch_data` para usar `requests.Session`, cabeceras tipo navegador y reintentos con backoff exponencial.
- **Estructura del Proyecto**: Estandarización en el uso de `python -m src.scraper` para asegurar importaciones de módulos consistentes.

### Corregido
- Mejora en el manejo de `ConnectionResetError` de la API de MINETUR mediante una gestión de sesiones adecuada.
- Estandarización de la codificación de caracteres (UTF-8) para Windows y entornos Unix.
