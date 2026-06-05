import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DATABASE_URL

def get_connection():
    """
    Establece y retorna la conexión a la base de datos PostgreSQL (local o nube).
    """
    if DATABASE_URL:
        # Si hay una URL en config.py, psycopg2 se conecta directamente con ella
        return psycopg2.connect(DATABASE_URL)
        
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def crear_base_de_datos_si_no_existe():
    """
    Crea la base de datos si no existe de forma local.
    Si se usa DATABASE_URL, asumimos que la base de datos ya fue creada en la nube.
    """
    if DATABASE_URL:
        print("-> Usando base de datos en la nube (DATABASE_URL activa). Omitiendo creación de DB.")
        return

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database="postgres"
    )
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute(f"CREATE DATABASE {DB_NAME};")
        print(f"[OK] Base de datos '{DB_NAME}' creada con éxito de forma local.")
    except psycopg2.errors.DuplicateDatabase:
        # Ya existe, no se hace nada
        pass
    finally:
        cur.close()
        conn.close()


def crear_esquema():
    """
    Crea las tablas relacionales del proyecto en PostgreSQL.
    """
    print("-> Creando tablas en PostgreSQL...")
    conn = get_connection()
    cur = conn.cursor()
    
    # DDL de Tablas de Dimensión
    ddl_municipios = """
    CREATE TABLE IF NOT EXISTS municipios (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        nombre_normalizado VARCHAR(100) UNIQUE NOT NULL
    );
    """
    
    ddl_contaminantes = """
    CREATE TABLE IF NOT EXISTS contaminantes (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(50) UNIQUE NOT NULL,
        nombre_display VARCHAR(100) NOT NULL
    );
    """
    
    ddl_grupos_diagnosticos = """
    CREATE TABLE IF NOT EXISTS grupos_diagnosticos (
        id SERIAL PRIMARY KEY,
        codigo_cie10 VARCHAR(50),
        nombre VARCHAR(255) UNIQUE NOT NULL,
        capitulo VARCHAR(255)
    );
    """
    
    # DDL de Tablas de Hechos (Fact Tables)
    ddl_analisis_riesgo = """
    CREATE TABLE IF NOT EXISTS analisis_riesgo (
        id SERIAL PRIMARY KEY,
        municipio_id INT REFERENCES municipios(id),
        grupo_diagnostico_id INT REFERENCES grupos_diagnosticos(id),
        contaminante_id INT REFERENCES contaminantes(id),
        tipo_rezago VARCHAR(50),
        numero_modelo INT,
        sexo VARCHAR(50),
        grupo_edad VARCHAR(100),
        casos INT,
        rezago VARCHAR(50),
        beta NUMERIC,
        exponencial_beta NUMERIC,
        limite_inferior NUMERIC,
        limite_superior NUMERIC,
        porcentaje_incremento_riesgo NUMERIC
    );
    """
    
    ddl_enfermedades = """
    CREATE TABLE IF NOT EXISTS enfermedades (
        id SERIAL PRIMARY KEY,
        municipio_id INT REFERENCES municipios(id),
        grupo_diagnostico_id INT REFERENCES grupos_diagnosticos(id),
        periodo INT,
        sexo VARCHAR(50),
        grupo_edad VARCHAR(100),
        casos INT
    );
    """
    
    ddl_tasa_mortalidad = """
    CREATE TABLE IF NOT EXISTS tasa_mortalidad (
        id SERIAL PRIMARY KEY,
        municipio_id INT REFERENCES municipios(id),
        anio INT,
        capitulo VARCHAR(255),
        sexo VARCHAR(50),
        tasa_ajustada NUMERIC
    );
    """
    
    ddl_defunciones = """
    CREATE TABLE IF NOT EXISTS defunciones (
        id SERIAL PRIMARY KEY,
        municipio_id INT REFERENCES municipios(id),
        grupo_diagnostico_id INT REFERENCES grupos_diagnosticos(id),
        periodo INT,
        sexo VARCHAR(50),
        grupo_edad VARCHAR(100),
        muertes NUMERIC
    );
    """
    
    ddl_mediciones_siata = """
    CREATE TABLE IF NOT EXISTS mediciones_siata (
        id SERIAL PRIMARY KEY,
        estacion VARCHAR(150) NOT NULL,
        pm25_ica NUMERIC,
        fecha_hora TIMESTAMP NOT NULL,
        latitud NUMERIC,
        longitud NUMERIC,
        categoria_ica VARCHAR(50),
        fecha_carga TIMESTAMP,
        UNIQUE (estacion, fecha_hora)
    );
    """
    
    try:
        cur.execute(ddl_municipios)
        cur.execute(ddl_contaminantes)
        cur.execute(ddl_grupos_diagnosticos)
        cur.execute(ddl_analisis_riesgo)
        cur.execute(ddl_enfermedades)
        cur.execute(ddl_tasa_mortalidad)
        cur.execute(ddl_defunciones)
        cur.execute(ddl_mediciones_siata)
        conn.commit()
        print("[OK] Tablas DDL creadas exitosamente en PostgreSQL.")
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Error al crear tablas: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

def poblar_dimensiones_basicas(conn):
    """
    Auto-pobla dimensiones fijas o iniciales para evitar inconsistencias de clave foránea.
    """
    cur = conn.cursor()
    try:
        # 1. Contaminantes
        contaminantes = [
            ('pm10', 'Material Particulado PM10'),
            ('pm25', 'Material Particulado PM2.5'),
            ('o3', 'Ozono O3')
        ]
        cur.executemany("""
            INSERT INTO contaminantes (nombre, nombre_display) 
            VALUES (%s, %s) ON CONFLICT (nombre) DO NOTHING;
        """, contaminantes)
        
        conn.commit()
    finally:
        cur.close()

def asegurar_municipios_y_diagnosticos(conn, municipios_lista, diagnosticos_lista):
    """
    Asegura que los municipios y diagnósticos existan en las tablas dimensiones
    y retorna diccionarios con sus correspondientes IDs.
    """
    cur = conn.cursor()
    
    # Insertar municipios
    for mun in municipios_lista:
        cur.execute("""
            INSERT INTO municipios (nombre, nombre_normalizado) 
            VALUES (%s, %s) ON CONFLICT (nombre_normalizado) DO NOTHING;
        """, (mun, mun))
    
    # Insertar diagnósticos
    for diag in diagnosticos_lista:
        # Extraer un CIE-10 básico si está en paréntesis al final del string, ej: "(H65-H75)"
        codigo_cie10 = None
        if '(' in diag and ')' in diag:
            partes = diag.split('(')
            codigo_cie10 = partes[-1].replace(')', '').strip()
        cur.execute("""
            INSERT INTO grupos_diagnosticos (nombre, codigo_cie10) 
            VALUES (%s, %s) ON CONFLICT (nombre) DO NOTHING;
        """, (diag, codigo_cie10))
        
    conn.commit()
    
    # Consultar mapeo de IDs de Municipios
    cur.execute("SELECT nombre_normalizado, id FROM municipios;")
    municipios_map = dict(cur.fetchall())
    
    # Consultar mapeo de IDs de Diagnósticos
    cur.execute("SELECT nombre, id FROM grupos_diagnosticos;")
    diagnosticos_map = dict(cur.fetchall())
    
    cur.close()
    return municipios_map, diagnosticos_map

def vaciar_tablas_hechos(conn):
    """
    Limpia las tablas de hechos antes de recargarlas para evitar duplicados históricos de CSVs.
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
    cur = conn.cursor()
    
    # Mapear contaminante a su ID
    cur.execute("SELECT nombre, id FROM contaminantes;")
    cont_map = dict(cur.fetchall())
    
    datos = []
    for idx, row in df.iterrows():
        m_id = municipios_map.get(row['municipio_normalizado'])
        g_id = diagnosticos_map.get(row['grupo_diagnostico'])
        c_id = cont_map.get(row['contaminante'].lower())
        
        datos.append((
            m_id, g_id, c_id, row['tipo_rezago'], row['numero_modelo'], row['sexo'],
            row['grupo_edad_normalizado'], row['casos'], row['rezago'], row['beta'],
            row['exponencial_beta'], row['limite_inferior'], row['limite_superior'],
            row['porcentaje_incremento_riesgo']
        ))
        
    query = """
        INSERT INTO analisis_riesgo (
            municipio_id, grupo_diagnostico_id, contaminante_id, tipo_rezago, numero_modelo,
            sexo, grupo_edad, casos, rezago, beta, exponencial_beta, limite_inferior,
            limite_superior, porcentaje_incremento_riesgo
        ) VALUES %s;
    """
    execute_values(cur, query, datos)
    conn.commit()
    cur.close()
    print(f"[OK] Cargada tabla analisis_riesgo con {len(df)} registros.")

def cargar_enfermedades(conn, df, municipios_map, diagnosticos_map):
    cur = conn.cursor()
    datos = []
    for idx, row in df.iterrows():
        m_id = municipios_map.get(row['municipio_normalizado'])
        g_id = diagnosticos_map.get(row['grupo'])
        
        datos.append((
            m_id, g_id, row['periodo'], row['sexo'], row['grupo_edad_normalizado'], row['casos']
        ))
        
    query = """
        INSERT INTO enfermedades (
            municipio_id, grupo_diagnostico_id, periodo, sexo, grupo_edad, casos
        ) VALUES %s;
    """
    execute_values(cur, query, datos)
    conn.commit()
    cur.close()
    print(f"[OK] Cargada tabla enfermedades con {len(df)} registros.")

def cargar_tasa_mortalidad(conn, df, municipios_map):
    cur = conn.cursor()
    datos = []
    for idx, row in df.iterrows():
        m_id = municipios_map.get(row['municipio_normalizado'])
        datos.append((
            m_id, row['anio'], row['capitulo'], row['sexo'], row['tasa_ajustada']
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
    cur = conn.cursor()
    datos = []
    for idx, row in df.iterrows():
        m_id = municipios_map.get(row['municipio_normalizado'])
        g_id = diagnosticos_map.get(row['grupo'])
        datos.append((
            m_id, g_id, row['periodo'], row['sexo'], row['grupo_edad_normalizado'], row['muertes']
        ))
        
    query = """
        INSERT INTO defunciones (
            municipio_id, grupo_diagnostico_id, periodo, sexo, grupo_edad, muertes
        ) VALUES %s;
    """
    execute_values(cur, query, datos)
    conn.commit()
    cur.close()
    print(f"[OK] Cargada tabla defunciones con {len(df)} registros.")

def crear_vista_datos_integrados(conn):
    """
    Crea (si no existe) o refresca la vista materializada 'vista_riesgo_integrado'.
    Esta vista consolida las tres fuentes (SIATA en vivo + riesgo histórico + municipios + enfermedades)
    en una sola tabla desnormalizada para consulta directa desde la API y el notebook.
    Ejecutar como paso final del pipeline ETL.
    """
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM pg_matviews WHERE matviewname = 'vista_riesgo_integrado'")
        existe = cur.fetchone()

        sql_vista = """
        CREATE MATERIALIZED VIEW IF NOT EXISTS vista_riesgo_integrado AS
        WITH ultima_siata AS (
            SELECT DISTINCT ON (estacion) 
                estacion, pm25_ica, categoria_ica, fecha_hora
            FROM mediciones_siata
            WHERE pm25_ica IS NOT NULL
            ORDER BY estacion, fecha_hora DESC
        )
        SELECT 
            m.id AS municipio_id,
            m.nombre_normalizado AS municipio,
            us.estacion AS estacion_siata,
            us.pm25_ica AS pm25_actual,
            us.categoria_ica,
            us.fecha_hora AS ultima_medicion,
            gd.id AS grupo_diagnostico_id,
            gd.nombre AS enfermedad,
            gd.codigo_cie10,
            ar.sexo,
            ar.grupo_edad,
            ar.beta AS coeficiente_riesgo,
            ar.porcentaje_incremento_riesgo AS incremento_basico_historico,
            ROUND((EXP(ar.beta * us.pm25_ica) - 1) * 100, 2) AS incremento_riesgo_pct_actual
        FROM ultima_siata us
        JOIN municipios m ON us.estacion ILIKE '%' || m.nombre_normalizado || '%'
        JOIN analisis_riesgo ar ON ar.municipio_id = m.id
        JOIN grupos_diagnosticos gd ON ar.grupo_diagnostico_id = gd.id
        JOIN contaminantes c ON ar.contaminante_id = c.id
        WHERE c.nombre = 'pm25'
        ORDER BY m.nombre_normalizado, ar.sexo, ar.grupo_edad;
        """

        if not existe:
            cur.execute(sql_vista)
            print("[OK] Vista materializada 'vista_riesgo_integrado' creada.")
        else:
            cur.execute("REFRESH MATERIALIZED VIEW vista_riesgo_integrado;")
            print("[OK] Vista materializada 'vista_riesgo_integrado' refrescada.")

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Al crear/refrescar vista integrada: {e}")
        raise
    finally:
        cur.close()


def cargar_mediciones_siata(conn, df):
    """
    Carga los datos de SIATA en tiempo real en la base de datos PostgreSQL.
    Implementa la estrategia UPSERT para evitar duplicados.
    """
    if df.empty:
        print("[WARNING] SIATA: No hay registros para cargar.")
        return
        
    cur = conn.cursor()
    datos = []
    for idx, row in df.iterrows():
        # Manejo de nulos en pm25 para Postgres
        pm25 = None if pd.isna(row['pm25_ica']) else row['pm25_ica']
        lat = None if pd.isna(row['latitud']) else row['latitud']
        lon = None if pd.isna(row['longitud']) else row['longitud']
        
        datos.append((
            row['estacion'], pm25, row['fecha_hora'], lat, lon,
            row['categoria_ica'], row['fecha_carga']
        ))
        
    # Query de UPSERT (ON CONFLICT DO NOTHING)
    query = """
        INSERT INTO mediciones_siata (
            estacion, pm25_ica, fecha_hora, latitud, longitud, categoria_ica, fecha_carga
        ) VALUES %s
        ON CONFLICT (estacion, fecha_hora) 
        DO NOTHING;
    """
    execute_values(cur, query, datos)
    conn.commit()
    cur.close()
    print(f"[OK] Cargados datos de SIATA en tiempo real (Idempotente) — {len(df)} estaciones procesadas.")
