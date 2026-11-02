"""
Esquema de Base de Datos (DDL)
================================
Creación de las tablas relacionales en PostgreSQL: tablas de dimensión
(catálogos compartidos) y tablas de hechos (datos medidos).

Relación con la metodología (respuesta a evaluadores)
------------------------------------------------------
La estructura de datos que los evaluadores solicitaron aclarar se define
aquí. El modelo sigue el esquema estrella (star schema):

    DIMENSIONES (catálogos compartidos entre todas las fuentes):
    ┌─────────────────────┐  ┌──────────────────┐  ┌───────────────────────┐
    │ municipios          │  │ contaminantes    │  │ grupos_diagnosticos   │
    │─────────────────────│  │──────────────────│  │───────────────────────│
    │ id (PK)             │  │ id (PK)          │  │ id (PK)               │
    │ nombre              │  │ nombre (UNIQUE)  │  │ codigo_cie10          │
    │ nombre_normalizado  │  │ nombre_display   │  │ nombre (UNIQUE)       │
    │ (UNIQUE)            │  │                  │  │ capitulo              │
    └─────────────────────┘  └──────────────────┘  └───────────────────────┘

    HECHOS (datos medidos, vinculados por FK a las dimensiones):
    ┌──────────────────────┐  ┌───────────────┐  ┌───────────────────┐
    │ analisis_riesgo      │  │ enfermedades  │  │ tasa_mortalidad   │
    │──────────────────────│  │───────────────│  │───────────────────│
    │ municipio_id (FK)    │  │ municipio_id  │  │ municipio_id (FK) │
    │ grupo_diag_id (FK)   │  │ grupo_diag_id │  │ anio              │
    │ contaminante_id (FK) │  │ periodo       │  │ capitulo          │
    │ beta, exponencial    │  │ sexo, edad    │  │ sexo              │
    │ limite_inf/sup       │  │ casos         │  │ tasa_ajustada     │
    └──────────────────────┘  └───────────────┘  └───────────────────┘

    ┌──────────────────────┐  ┌──────────────────────────────────────┐
    │ defunciones          │  │ mediciones_siata                     │
    │──────────────────────│  │──────────────────────────────────────│
    │ municipio_id (FK)    │  │ estacion                             │
    │ grupo_diag_id (FK)   │  │ pm25_ica                             │
    │ periodo, sexo, edad  │  │ fecha_hora                           │
    │ muertes              │  │ latitud, longitud                    │
    │                      │  │ categoria_ica                        │
    │                      │  │ UNIQUE(estacion, fecha_hora) ← UPSERT│
    └──────────────────────┘  └──────────────────────────────────────┘
"""

from etl.carga.conexion import get_connection


def crear_esquema():
    """
    Crea todas las tablas relacionales del proyecto en PostgreSQL.
    Usa IF NOT EXISTS para ser idempotente.
    """
    print("-> Creando tablas en PostgreSQL...")
    conn = get_connection()
    cur = conn.cursor()

    # ══════════════════════════════════════════════════════════════════════
    # TABLAS DE DIMENSIÓN (Catálogos compartidos)
    # ══════════════════════════════════════════════════════════════════════

    ddl_municipios = """
    CREATE TABLE IF NOT EXISTS municipios (
        id                  SERIAL PRIMARY KEY,
        nombre              VARCHAR(100) NOT NULL,
        nombre_normalizado  VARCHAR(100) UNIQUE NOT NULL
    );
    """

    ddl_contaminantes = """
    CREATE TABLE IF NOT EXISTS contaminantes (
        id              SERIAL PRIMARY KEY,
        nombre          VARCHAR(50) UNIQUE NOT NULL,
        nombre_display  VARCHAR(100) NOT NULL
    );
    """

    ddl_grupos_diagnosticos = """
    CREATE TABLE IF NOT EXISTS grupos_diagnosticos (
        id           SERIAL PRIMARY KEY,
        codigo_cie10 VARCHAR(50),
        nombre       VARCHAR(255) UNIQUE NOT NULL,
        capitulo     VARCHAR(255)
    );
    """

    # ══════════════════════════════════════════════════════════════════════
    # TABLAS DE HECHOS (Datos medidos, vinculados por FK)
    # ══════════════════════════════════════════════════════════════════════

    ddl_analisis_riesgo = """
    CREATE TABLE IF NOT EXISTS analisis_riesgo (
        id                          SERIAL PRIMARY KEY,
        municipio_id                INT REFERENCES municipios(id),
        grupo_diagnostico_id        INT REFERENCES grupos_diagnosticos(id),
        contaminante_id             INT REFERENCES contaminantes(id),
        tipo_rezago                 VARCHAR(50),
        numero_modelo               INT,
        sexo                        VARCHAR(50),
        grupo_edad                  VARCHAR(100),
        casos                       INT,
        rezago                      VARCHAR(50),
        beta                        NUMERIC,
        exponencial_beta            NUMERIC,
        limite_inferior             NUMERIC,
        limite_superior             NUMERIC,
        porcentaje_incremento_riesgo NUMERIC
    );
    """

    ddl_enfermedades = """
    CREATE TABLE IF NOT EXISTS enfermedades (
        id                   SERIAL PRIMARY KEY,
        municipio_id         INT REFERENCES municipios(id),
        grupo_diagnostico_id INT REFERENCES grupos_diagnosticos(id),
        periodo              INT,
        sexo                 VARCHAR(50),
        grupo_edad           VARCHAR(100),
        casos                INT
    );
    """

    ddl_tasa_mortalidad = """
    CREATE TABLE IF NOT EXISTS tasa_mortalidad (
        id             SERIAL PRIMARY KEY,
        municipio_id   INT REFERENCES municipios(id),
        anio           INT,
        capitulo       VARCHAR(255),
        sexo           VARCHAR(50),
        tasa_ajustada  NUMERIC
    );
    """

    ddl_defunciones = """
    CREATE TABLE IF NOT EXISTS defunciones (
        id                   SERIAL PRIMARY KEY,
        municipio_id         INT REFERENCES municipios(id),
        grupo_diagnostico_id INT REFERENCES grupos_diagnosticos(id),
        periodo              INT,
        sexo                 VARCHAR(50),
        grupo_edad           VARCHAR(100),
        muertes              NUMERIC
    );
    """

    ddl_mediciones_siata = """
    CREATE TABLE IF NOT EXISTS mediciones_siata (
        id            SERIAL PRIMARY KEY,
        estacion      VARCHAR(150) NOT NULL,
        pm25_ica      NUMERIC,
        fecha_hora    TIMESTAMP NOT NULL,
        latitud       NUMERIC,
        longitud      NUMERIC,
        categoria_ica VARCHAR(50),
        fecha_carga   TIMESTAMP,
        UNIQUE (estacion, fecha_hora)
    );
    """

    try:
        # Crear dimensiones primero (por integridad referencial)
        cur.execute(ddl_municipios)
        cur.execute(ddl_contaminantes)
        cur.execute(ddl_grupos_diagnosticos)

        # Crear hechos después (dependen de las dimensiones)
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
