"""
Módulo de Extracción — FASE 1 del Pipeline ETL
================================================
Identificación y extracción de las fuentes de datos heterogéneas:

    Fuente Primaria (Sensor):
        API SIATA → Feed KML con mediciones de PM2.5 en tiempo real
                     de ~23 estaciones del Valle de Aburrá.

    Fuentes Secundarias (Archivos):
        4 archivos CSV del portal de datos abiertos del AMVA (2008-2017):
        - AnalisisRiesgo: coeficientes epidemiológicos beta (β)
        - EnfermedadesCalculadas: casos de morbilidad por diagnóstico CIE-10
        - TasaMortalidad: tasas de mortalidad ajustadas por municipio
        - DefunsionesCalculadas: conteo de defunciones por causa

Archivos de este módulo
-----------------------
    siata_api.py  →  Extracción de la API SIATA (peticiones HTTP GET + parseo KML)
"""

from etl.extraccion.siata_api import extraer_siata
