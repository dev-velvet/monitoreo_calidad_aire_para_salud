"""
Configuración del Sistema
=========================
Parámetros de conexión a PostgreSQL, URL de la API SIATA y rutas
a los archivos CSV fuente.

Relación con la metodología
---------------------------
Este módulo centraliza los parámetros que hacen al pipeline REPRODUCIBLE:
- Dirección de la base de datos PostgreSQL (local o nube Neon.tech)
- URL oficial del feed KML de la API SIATA para PM2.5
- Rutas a los 4 archivos CSV de datos epidemiológicos históricos (2008-2017)
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# CONEXIÓN A BASE DE DATOS POSTGRESQL
# ─────────────────────────────────────────────────────────────────────────────
# Si se usa un servicio en la nube (Neon.tech, Render), configurar DATABASE_URL.
# Si se usa PostgreSQL local, configurar las variables individuales.

DATABASE_URL = os.getenv("DATABASE_URL", "")

DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "5432")
DB_USER     = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME     = os.getenv("DB_NAME", "calidad_aire_salud")

# ─────────────────────────────────────────────────────────────────────────────
# RUTAS DE ARCHIVOS
# ─────────────────────────────────────────────────────────────────────────────
# BASE_DIR apunta a la carpeta backend/ (raíz del código fuente).
# DATOS_CRUDOS_DIR contiene los 4 CSVs históricos del portal de datos abiertos del AMVA,
# organizados como anexos del proyecto.

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATOS_CRUDOS_DIR = os.path.join(BASE_DIR, "anexos", "datos", "crudos")

CSV_ANALISIS_RIESGO  = os.path.join(DATOS_CRUDOS_DIR, "AnalisisRiesgo_20082017.csv")
CSV_ENFERMEDADES     = os.path.join(DATOS_CRUDOS_DIR, "EnfermedadesCalculadas_2008-2017.csv")
CSV_TASA_MORTALIDAD  = os.path.join(DATOS_CRUDOS_DIR, "TasaMortalidad_2008-2017.csv")
CSV_DEFUNCIONES      = os.path.join(DATOS_CRUDOS_DIR, "DefunsionesCalculadas_2008-2017.csv")

# ─────────────────────────────────────────────────────────────────────────────
# API SIATA (FUENTE PRIMARIA — SENSOR EN TIEMPO REAL)
# ─────────────────────────────────────────────────────────────────────────────
# Feed KML oficial de la red de monitoreo de calidad del aire del SIATA.
# Retorna las mediciones de PM2.5 de ~23 estaciones del Valle de Aburrá.
# Frecuencia de actualización del sensor: cada 2 minutos.

SIATA_API_URL = "https://www.siata.gov.co/kml/01_Redes/AMVARedAire/RedAireAMVA_PM25.kml"
