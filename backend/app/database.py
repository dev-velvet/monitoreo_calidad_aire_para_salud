"""
Módulo de conexión a la base de datos PostgreSQL (Neon).
Compatible con variables de entorno de Render.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from dotenv import load_dotenv

# Cargar .env si existe (desarrollo local); en Render se ignora y usa env vars directas
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env_path = os.path.join(_backend_dir, ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path)
load_dotenv()  # Fallback a cwd

DATABASE_URL = os.getenv("DATABASE_URL", "")


def get_connection():
    """
    Retorna una conexión activa a PostgreSQL usando DATABASE_URL.
    Usa RealDictCursor para que las filas se retornen como diccionarios.
    """
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL no está configurada. "
            "Configúrala como variable de entorno o en el archivo .env"
        )
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


@contextmanager
def get_db():
    """
    Context manager para obtener una conexión y cerrarla automáticamente.
    Uso:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT ...")
    """
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
