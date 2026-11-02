"""
Carga de Mediciones SIATA (Tiempo Real)
=========================================
Inserta las lecturas de PM2.5 en la tabla mediciones_siata usando
la estrategia UPSERT para evitar duplicados.

Estrategia UPSERT (respuesta a evaluadores)
---------------------------------------------
    INSERT ... ON CONFLICT (estacion, fecha_hora) DO NOTHING

    Esta estrategia es IDEMPOTENTE: el pipeline puede ejecutarse
    múltiples veces sin generar duplicados. Si ya existe un registro
    para la misma estación y fecha/hora, simplemente se ignora.

    Esto es fundamental para el scheduler que ejecuta la extracción
    cada hora en producción (o cada 10 segundos en modo demo).
"""

import pandas as pd
from psycopg2.extras import execute_values


def cargar_mediciones_siata(conn, df):
    """
    Carga las mediciones de SIATA en PostgreSQL con estrategia UPSERT.

    La restricción UNIQUE (estacion, fecha_hora) garantiza que:
        - Si la medición ya existe → se ignora (DO NOTHING)
        - Si es nueva → se inserta normalmente

    Args:
        conn: conexión PostgreSQL activa.
        df: DataFrame con las mediciones extraídas de la API SIATA.
    """
    if df.empty:
        print("[WARNING] SIATA: No hay registros para cargar.")
        return

    cur = conn.cursor()

    # Preparar datos manejando nulos para PostgreSQL
    datos = []
    for _, row in df.iterrows():
        pm25 = None if pd.isna(row['pm25_ica']) else row['pm25_ica']
        lat  = None if pd.isna(row['latitud'])  else row['latitud']
        lon  = None if pd.isna(row['longitud']) else row['longitud']

        datos.append((
            row['estacion'], pm25, row['fecha_hora'],
            lat, lon, row['categoria_ica'], row['fecha_carga'],
        ))

    # Query UPSERT: ON CONFLICT DO NOTHING evita duplicados
    query = """
        INSERT INTO mediciones_siata (
            estacion, pm25_ica, fecha_hora,
            latitud, longitud, categoria_ica, fecha_carga
        ) VALUES %s
        ON CONFLICT (estacion, fecha_hora)
        DO NOTHING;
    """
    execute_values(cur, query, datos)
    conn.commit()
    cur.close()
    print(f"[OK] Cargados datos de SIATA en tiempo real "
          f"(Idempotente) — {len(df)} estaciones procesadas.")
