"""
Población de Tablas de Dimensión
==================================
Carga los catálogos compartidos que actúan como llaves de integración
entre las diferentes fuentes de datos.

Relación con la metodología
---------------------------
Las tablas de dimensión son el MECANISMO DE INTEGRACIÓN que resuelve
la pregunta de los evaluadores: "¿cómo se integran las estaciones
con la información epidemiológica?"

    municipios          →  vincula estaciones SIATA con datos de salud
    contaminantes       →  filtra los análisis de riesgo por tipo (PM2.5)
    grupos_diagnosticos →  conecta riesgo con enfermedades y defunciones
"""

from psycopg2.extras import execute_values


def poblar_dimensiones_basicas(conn):
    """
    Carga los contaminantes fijos (PM10, PM2.5, O3) en la tabla de dimensión.
    Usa ON CONFLICT DO NOTHING para ser idempotente.
    """
    cur = conn.cursor()
    try:
        contaminantes = [
            ('pm10', 'Material Particulado PM10'),
            ('pm25', 'Material Particulado PM2.5'),
            ('o3',   'Ozono O3'),
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
    Inserta los municipios y diagnósticos únicos extraídos de todos los
    datasets y retorna los mapeos {nombre → id} para resolver las claves
    foráneas de las tablas de hechos.

    Este paso es CRÍTICO para la integración:
        - Cada municipio recibe un ID único en la dimensión
        - Cada diagnóstico CIE-10 recibe un ID único
        - Las tablas de hechos usan estos IDs como FK

    Args:
        conn: conexión PostgreSQL activa.
        municipios_lista: list de nombres de municipios únicos de los 4 CSVs.
        diagnosticos_lista: list de nombres de diagnósticos únicos.

    Returns:
        tuple: (municipios_id_map, diagnosticos_id_map)
            municipios_id_map: dict {nombre_normalizado: id}
            diagnosticos_id_map: dict {nombre_diagnostico: id}
    """
    cur = conn.cursor()

    # ── Insertar municipios ────────────────────────────────────────────────
    for mun in municipios_lista:
        cur.execute("""
            INSERT INTO municipios (nombre, nombre_normalizado)
            VALUES (%s, %s) ON CONFLICT (nombre_normalizado) DO NOTHING;
        """, (mun, mun))

    # ── Insertar diagnósticos (con extracción de código CIE-10) ────────────
    for diag in diagnosticos_lista:
        codigo_cie10 = None
        if '(' in diag and ')' in diag:
            partes = diag.split('(')
            codigo_cie10 = partes[-1].replace(')', '').strip()
        cur.execute("""
            INSERT INTO grupos_diagnosticos (nombre, codigo_cie10)
            VALUES (%s, %s) ON CONFLICT (nombre) DO NOTHING;
        """, (diag, codigo_cie10))

    conn.commit()

    # ── Obtener mapeos de IDs ──────────────────────────────────────────────
    cur.execute("SELECT nombre_normalizado, id FROM municipios;")
    municipios_map = dict(cur.fetchall())

    cur.execute("SELECT nombre, id FROM grupos_diagnosticos;")
    diagnosticos_map = dict(cur.fetchall())

    cur.close()
    return municipios_map, diagnosticos_map
