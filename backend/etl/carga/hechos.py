"""
Carga de Tablas de Hechos (Datos Históricos)
==============================================
Inserta los datos de los 4 CSVs históricos (2008-2017) en las tablas
de hechos de PostgreSQL, vinculándolos con las dimensiones por FK.

Estrategia de carga
-------------------
    TRUNCATE + INSERT (recarga limpia):
    - Se vacían las tablas de hechos antes de cada carga
    - Se reinsertan todos los registros limpios
    - Esto garantiza consistencia sin acumular duplicados
    - Operación idempotente: ejecutable múltiples veces sin efecto adverso
"""

from psycopg2.extras import execute_values


def vaciar_tablas_hechos(conn):
    """
    Vacía las tablas de hechos antes de la recarga para evitar
    duplicados históricos de CSVs.
    """
    cur = conn.cursor()
    try:
        cur.execute("TRUNCATE TABLE analisis_riesgo CASCADE;")
        cur.execute("TRUNCATE TABLE enfermedades CASCADE;")
        cur.execute("TRUNCATE TABLE tasa_mortalidad CASCADE;")
        cur.execute("TRUNCATE TABLE defunciones CASCADE;")
        conn.commit()
        print("[OK] Tablas de hechos vaciadas para recarga limpia.")
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Error al vaciar hechos: {e}")
    finally:
        cur.close()


def cargar_analisis_riesgo(conn, df, municipios_map, diagnosticos_map):
    """
    Carga los coeficientes β epidemiológicos en la tabla analisis_riesgo.

    Los coeficientes β son el parámetro central del cálculo de riesgo:
        ΔR = (e^(β × PM2.5/10) − 1) × 100

    Args:
        conn: conexión PostgreSQL.
        df: DataFrame limpio de AnalisisRiesgo.
        municipios_map: dict {nombre → id} de municipios.
        diagnosticos_map: dict {nombre → id} de diagnósticos.
    """
    cur = conn.cursor()

    # Obtener mapeo de contaminantes
    cur.execute("SELECT nombre, id FROM contaminantes;")
    cont_map = dict(cur.fetchall())

    datos = []
    for _, row in df.iterrows():
        m_id = municipios_map.get(row['municipio_normalizado'])
        g_id = diagnosticos_map.get(row['grupo_diagnostico'])
        c_id = cont_map.get(row['contaminante'].lower())

        datos.append((
            m_id, g_id, c_id, row['tipo_rezago'], row['numero_modelo'],
            row['sexo'], row['grupo_edad_normalizado'], row['casos'],
            row['rezago'], row['beta'], row['exponencial_beta'],
            row['limite_inferior'], row['limite_superior'],
            row['porcentaje_incremento_riesgo'],
        ))

    query = """
        INSERT INTO analisis_riesgo (
            municipio_id, grupo_diagnostico_id, contaminante_id,
            tipo_rezago, numero_modelo, sexo, grupo_edad, casos,
            rezago, beta, exponencial_beta, limite_inferior,
            limite_superior, porcentaje_incremento_riesgo
        ) VALUES %s;
    """
    execute_values(cur, query, datos)
    conn.commit()
    cur.close()
    print(f"[OK] Cargada tabla analisis_riesgo con {len(df)} registros.")


def cargar_enfermedades(conn, df, municipios_map, diagnosticos_map):
    """
    Carga los casos de morbilidad en la tabla enfermedades.
    """
    cur = conn.cursor()
    datos = []
    for _, row in df.iterrows():
        m_id = municipios_map.get(row['municipio_normalizado'])
        g_id = diagnosticos_map.get(row['grupo'])
        datos.append((
            m_id, g_id, row['periodo'], row['sexo'],
            row['grupo_edad_normalizado'], row['casos'],
        ))

    query = """
        INSERT INTO enfermedades (
            municipio_id, grupo_diagnostico_id, periodo,
            sexo, grupo_edad, casos
        ) VALUES %s;
    """
    execute_values(cur, query, datos)
    conn.commit()
    cur.close()
    print(f"[OK] Cargada tabla enfermedades con {len(df)} registros.")


def cargar_tasa_mortalidad(conn, df, municipios_map):
    """
    Carga las tasas de mortalidad ajustadas en la tabla tasa_mortalidad.
    """
    cur = conn.cursor()
    datos = []
    for _, row in df.iterrows():
        m_id = municipios_map.get(row['municipio_normalizado'])
        datos.append((
            m_id, row['anio'], row['capitulo'],
            row['sexo'], row['tasa_ajustada'],
        ))

    query = """
        INSERT INTO tasa_mortalidad (
            municipio_id, anio, capitulo, sexo, tasa_ajustada
        ) VALUES %s;
    """
    execute_values(cur, query, datos)
    conn.commit()
    cur.close()
    print(f"[OK] Cargada tabla tasa_mortalidad con {len(df)} registros.")


def cargar_defunciones(conn, df, municipios_map, diagnosticos_map):
    """
    Carga el conteo de defunciones en la tabla defunciones.
    """
    cur = conn.cursor()
    datos = []
    for _, row in df.iterrows():
        m_id = municipios_map.get(row['municipio_normalizado'])
        g_id = diagnosticos_map.get(row['grupo'])
        datos.append((
            m_id, g_id, row['periodo'], row['sexo'],
            row['grupo_edad_normalizado'], row['muertes'],
        ))

    query = """
        INSERT INTO defunciones (
            municipio_id, grupo_diagnostico_id, periodo,
            sexo, grupo_edad, muertes
        ) VALUES %s;
    """
    execute_values(cur, query, datos)
    conn.commit()
    cur.close()
    print(f"[OK] Cargada tabla defunciones con {len(df)} registros.")
