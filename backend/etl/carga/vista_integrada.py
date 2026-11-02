"""
Vista Materializada — Integración de las 3 Fuentes
=====================================================
Crea la vista consolidada `vista_riesgo_integrado` que unifica:
    1. Mediciones en tiempo real de SIATA (PM2.5)
    2. Coeficientes epidemiológicos históricos (β)
    3. Catálogos de municipios y diagnósticos

Relación con la metodología (respuesta a evaluadores)
------------------------------------------------------
Esta vista es el RESULTADO CENTRAL de la integración. Responde a las
preguntas de los evaluadores sobre cómo se vinculan las estaciones
con los datos epidemiológicos:

    Integración geográfica:
        Las estaciones SIATA se vinculan a municipios mediante:
            JOIN municipios m ON estacion ILIKE '%' || m.nombre_normalizado || '%'
        Ejemplo: "MED-UPAR Tráfico Centro" coincide con "Medellín"

    Función de agregación temporal:
        Se usa DISTINCT ON (estacion) ORDER BY fecha_hora DESC
        para seleccionar la MEDICIÓN MÁS RECIENTE por estación.
        NO se usa promedio, suma ni mediana.

    Cálculo de riesgo en tiempo real:
        La vista calcula el incremento de riesgo usando la fórmula:
            incremento_riesgo_pct_actual = ROUND((EXP(β × PM2.5/10) - 1) × 100, 2)
"""


def crear_vista_datos_integrados(conn):
    """
    Crea o refresca la vista materializada 'vista_riesgo_integrado'.

    La vista ejecuta un JOIN entre 4 tablas:
        mediciones_siata → municipios → analisis_riesgo → grupos_diagnosticos

    Resultado: una tabla desnormalizada con una fila por cada combinación de
    estación × enfermedad × sexo × grupo_edad, incluyendo el PM2.5 actual
    y el incremento de riesgo calculado en tiempo real.
    """
    cur = conn.cursor()
    try:
        # ── Verificar si la vista ya existe ────────────────────────────────
        cur.execute(
            "SELECT 1 FROM pg_matviews WHERE matviewname = 'vista_riesgo_integrado'"
        )
        existe = cur.fetchone()

        # ── SQL de la vista materializada ──────────────────────────────────
        sql_vista = """
        CREATE MATERIALIZED VIEW IF NOT EXISTS vista_riesgo_integrado AS

        -- CTE 1: Seleccionar la medición MÁS RECIENTE por estación
        -- (Función de agregación temporal: NO promedio, se toma el dato más actual)
        WITH ultima_siata AS (
            SELECT DISTINCT ON (estacion)
                estacion, pm25_ica, categoria_ica, fecha_hora
            FROM mediciones_siata
            WHERE pm25_ica IS NOT NULL
            ORDER BY estacion, fecha_hora DESC
        ),

        -- CTE 2: Vincular cada estación con su municipio
        -- (Integración geográfica: JOIN textual normalizado)
        estacion_por_municipio AS (
            SELECT DISTINCT ON (m.id)
                m.id                    AS municipio_id,
                m.nombre_normalizado    AS municipio,
                us.estacion             AS estacion_siata,
                us.pm25_ica             AS pm25_actual,
                us.categoria_ica,
                us.fecha_hora           AS ultima_medicion
            FROM ultima_siata us
            JOIN municipios m
                ON us.estacion ILIKE '%%' || m.nombre_normalizado || '%%'
            ORDER BY m.id, us.fecha_hora DESC
        )

        -- Consulta final: cruzar PM2.5 actual con coeficientes β históricos
        SELECT
            em.municipio_id,
            em.municipio,
            em.estacion_siata,
            em.pm25_actual,
            em.categoria_ica,
            em.ultima_medicion,
            gd.id           AS grupo_diagnostico_id,
            gd.nombre       AS enfermedad,
            gd.codigo_cie10,
            ar.sexo,
            ar.grupo_edad,
            ar.beta         AS coeficiente_riesgo,
            ar.porcentaje_incremento_riesgo AS incremento_basico_historico,
            -- FÓRMULA DE RIESGO: ΔR = (e^(β × PM2.5/10) − 1) × 100
            ROUND(
                (EXP(ar.beta * (em.pm25_actual / 10.0)) - 1) * 100, 2
            ) AS incremento_riesgo_pct_actual
        FROM estacion_por_municipio em
        JOIN analisis_riesgo ar      ON ar.municipio_id = em.municipio_id
        JOIN grupos_diagnosticos gd  ON ar.grupo_diagnostico_id = gd.id
        JOIN contaminantes c         ON ar.contaminante_id = c.id
        WHERE c.nombre = 'pm25'
        ORDER BY em.municipio, ar.sexo, ar.grupo_edad;
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
