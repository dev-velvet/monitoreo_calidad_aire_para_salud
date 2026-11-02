"""
Módulo de Configuración Centralizada
=====================================
Contiene todos los parámetros del sistema: conexión a base de datos,
URLs de APIs, rutas de archivos fuente y diccionarios de normalización.
"""

from etl.configuracion.settings import (
    DATABASE_URL,
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
    BASE_DIR,
    DATOS_CRUDOS_DIR,
    CSV_ANALISIS_RIESGO,
    CSV_ENFERMEDADES,
    CSV_TASA_MORTALIDAD,
    CSV_DEFUNCIONES,
    SIATA_API_URL,
)

from etl.configuracion.diccionarios import (
    MUNICIPIOS_MAPA,
    EDADES_MAPA,
)
