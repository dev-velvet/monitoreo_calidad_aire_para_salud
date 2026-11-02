"""
Conexión a Base de Datos PostgreSQL
=====================================
Gestiona la conexión al motor relacional PostgreSQL, ya sea local
o en la nube (Neon.tech / Render).

Relación con la metodología
---------------------------
PostgreSQL fue elegido como motor de almacenamiento porque:
    1. Soporta JOINs complejos entre datos de sensores y coeficientes β
    2. Permite vistas materializadas para la integración de fuentes
    3. Ofrece restricciones UNIQUE para la estrategia UPSERT
    4. Tiene extensión PostGIS para futuras consultas espaciales
"""

import psycopg2
from psycopg2.extras import execute_values

from etl.configuracion.settings import (
    DATABASE_URL, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME,
)


def get_connection():
    """
    Establece y retorna una conexión activa a PostgreSQL.

    Prioridad de conexión:
        1. Si DATABASE_URL está configurada → conexión directa a nube
        2. Si no → conexión local con host/port/user/password

    Returns:
        psycopg2.connection: conexión activa a PostgreSQL.
    """
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )


def crear_base_de_datos_si_no_existe():
    """
    Crea la base de datos 'calidad_aire_salud' si no existe (solo en local).
    Si se usa DATABASE_URL (nube), se asume que la BD ya fue creada.
    """
    if DATABASE_URL:
        print("-> Usando base de datos en la nube (DATABASE_URL activa). "
              "Omitiendo creación de DB.")
        return

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database="postgres",
    )
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute(f"CREATE DATABASE {DB_NAME};")
        print(f"[OK] Base de datos '{DB_NAME}' creada con éxito de forma local.")
    except psycopg2.errors.DuplicateDatabase:
        pass  # Ya existe, no se hace nada
    finally:
        cur.close()
        conn.close()
