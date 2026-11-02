# Herramienta de Integración ETL

La herramienta elegida fue **Python** con **Pandas** para transformación y limpieza, **PostgreSQL** como base de datos y **FastAPI** para exponer los datos.

Python fue la opción adecuada por su ecosistema de librerías. Pandas permitió leer y normalizar los CSVs históricos, corregir decimales mal formateados, unificar nombres de municipios y categorizar edades. Requests y ElementTree facilitaron la conexión HTTP con la API de SIATA para extraer datos en tiempo real. Psycopg2 posibilitó la carga estructurada en PostgreSQL. El motor relacional permitió diseñar tablas de dimensión y hechos conectadas por identificadores, cruzando mediciones actuales de PM2.5 con coeficientes históricos de riesgo mediante JOINs. FastAPI sirvió como puente entre la base de datos y el dashboard entregando los datos en JSON. Todo el pipeline se automatizó con schedule y threading.
