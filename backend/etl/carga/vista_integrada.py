"""
Vista Materializada — Integración de las 3 Fuentes (Promedio Móvil 24 Horas)
=============================================================================
Crea la vista consolidada `vista_riesgo_integrado` que unifica:
    1. Mediciones de SIATA (Promedio móvil 24 h y última lectura puntual)
    2. Coeficientes epidemiológicos históricos (β) e intervalos de confianza (95%)
    3. Catálogos de municipios y diagnósticos

Relación con la metodología y respuesta a evaluadores
------------------------------------------------------
Esta vista es el RESULTADO CENTRAL de la integración. Responde a las
observaciones metodológicas de los evaluadores y planes de mejoramiento:

    Integración geográfica:
        Las estaciones SIATA se vinculan a municipios mediante:
            JOIN municipios m ON estacion ILIKE '%' || m.nombre_normalizado || '%'
        Ejemplo: "MED-UPAR Tráfico Centro" coincide con "Medellín"

    Función de agregación temporal (Transición a 24 Horas):
        Se adopta el PROMEDIO MÓVIL DE LAS ÚLTIMAS 24 HORAS como métrica
        de exposición base para el cálculo del riesgo epidemiológico. Esto garantiza:
            1. Coherencia biológica y estadística con los coeficientes β del modelo
               GAM-Poisson (Grisales-Romero et al., 2022), los cuales fueron estimados
               a partir de concentraciones diarias de 24 horas.
            2. Coherencia normativa con la Resolución 2254 de 2017 (Colombia) y
               las Guías de Calidad del Aire de la OMS (2021).
        Asimismo, se preserva la MEDICIÓN MÁS RECIENTE (`pm25_actual`) como dato
        informativo puntual de alerta en vivo.

    Cálculo de riesgo y propagación de incertidumbre:
        La vista calcula el incremento relativo del riesgo poblacional mediante:
            incremento_riesgo_pct_24h = ROUND((EXP(β × PM2.5_24h / 10) - 1) × 100, 2)
        E incorpora los límites de confianza inferior y superior (IC 95%) derivados
        de los parámetros epidemiológicos `limite_inferior` y `limite_superior`.
"""


def crear_vista_datos_integrados(conn):
    """
    Crea o refresca la vista materializada 'vista_riesgo_integrado'.

    La vista ejecuta un JOIN entre 4 tablas:
        mediciones_siata → municipios → analisis_riesgo → grupos_diagnosticos

    Resultado: una tabla desnormalizada con una fila por cada combinación de
    estación × enfermedad × sexo × grupo_edad, incluyendo la exposición de 24 h,
    la lectura en vivo, el número de observaciones temporales y el incremento de riesgo.
    """
    cur = conn.cursor()
    try:
        # ── SQL de la vista materializada con Promedio Móvil 24 h ─────────────
        sql_vista = """
        DROP MATERIALIZED VIEW IF EXISTS vista_riesgo_integrado CASCADE;

        CREATE MATERIALIZED VIEW vista_riesgo_integrado AS

        -- CTE 1: Última medición puntual disponible por estación (Informativo en vivo)
        WITH ultima_siata AS (
            SELECT DISTINCT ON (estacion)
                estacion,
                pm25_ica AS pm25_actual,
                categoria_ica AS categoria_ica_actual,
                fecha_hora AS ultima_medicion
            FROM mediciones_siata
            WHERE pm25_ica IS NOT NULL
            ORDER BY estacion, fecha_hora DESC
        ),

        -- CTE 2: Promedio móvil de las últimas 24 horas por estación
        -- Ventana temporal: 24 horas previas a la fecha más reciente registrada
        ventana_24h AS (
            SELECT
                estacion,
                ROUND(AVG(pm25_ica)::numeric, 2) AS pm25_promedio_24h,
                COUNT(pm25_ica)                  AS n_lecturas_24h,
                MAX(pm25_ica)                    AS pm25_max_24h,
                MIN(pm25_ica)                    AS pm25_min_24h
            FROM mediciones_siata
            WHERE pm25_ica IS NOT NULL
              AND pm25_ica >= 0
              AND fecha_hora >= (
                  SELECT COALESCE(MAX(fecha_hora) - INTERVAL '24 hours', NOW() - INTERVAL '24 hours')
                  FROM mediciones_siata
              )
            GROUP BY estacion
        ),

        -- CTE 3: Consolidar métrica instantánea y promedio 24 h por estación
        estacion_metricas AS (
            SELECT
                u.estacion,
                u.pm25_actual,
                u.categoria_ica_actual,
                u.ultima_medicion,
                COALESCE(v.pm25_promedio_24h, u.pm25_actual) AS pm25_promedio_24h,
                COALESCE(v.n_lecturas_24h, 1)                AS n_lecturas_24h,
                -- Clasificación ICA oficial sobre el promedio de 24 horas (Resolución 2254 de 2017)
                CASE
                    WHEN COALESCE(v.pm25_promedio_24h, u.pm25_actual) <= 12.0 THEN 'Buena'
                    WHEN COALESCE(v.pm25_promedio_24h, u.pm25_actual) <= 37.0 THEN 'Moderada'
                    WHEN COALESCE(v.pm25_promedio_24h, u.pm25_actual) <= 55.0 THEN 'Dañina a la salud de grupos sensibles'
                    WHEN COALESCE(v.pm25_promedio_24h, u.pm25_actual) <= 150.0 THEN 'Dañina para la salud'
                    WHEN COALESCE(v.pm25_promedio_24h, u.pm25_actual) <= 250.0 THEN 'Muy dañina para la salud'
                    ELSE 'Peligrosa'
                END AS categoria_ica_24h
            FROM ultima_siata u
            LEFT JOIN ventana_24h v ON u.estacion = v.estacion
        ),

        -- CTE 4: Vincular cada estación con su municipio
        estacion_por_municipio AS (
            SELECT DISTINCT ON (m.id)
                m.id                    AS municipio_id,
                m.nombre_normalizado    AS municipio,
                em.estacion             AS estacion_siata,
                em.pm25_actual,
                em.categoria_ica_actual,
                em.pm25_promedio_24h,
                em.categoria_ica_24h    AS categoria_ica,
                em.n_lecturas_24h,
                em.ultima_medicion
            FROM estacion_metricas em
            JOIN municipios m
                ON em.estacion ILIKE '%%' || m.nombre_normalizado || '%%'
            ORDER BY m.id, em.ultima_medicion DESC
        )

        -- Consulta final: cruzar exposición de 24 horas con coeficientes β históricos
        SELECT
            em.municipio_id,
            em.municipio,
            em.estacion_siata,
            em.pm25_actual,
            em.pm25_promedio_24h,
            em.n_lecturas_24h,
            em.categoria_ica,
            em.categoria_ica_actual,
            em.ultima_medicion,
            gd.id           AS grupo_diagnostico_id,
            gd.nombre       AS enfermedad,
            gd.codigo_cie10,
            ar.sexo,
            ar.grupo_edad,
            ar.beta         AS coeficiente_riesgo,
            ar.limite_inferior,
            ar.limite_superior,
            ar.porcentaje_incremento_riesgo AS incremento_basico_historico,
            -- FÓRMULA DE RIESGO COHERENTE CON MODELO GAM (Promedio 24 h):
            -- ΔR = (e^(β × PM2.5_24h / 10) − 1) × 100
            ROUND(
                (EXP(ar.beta * (em.pm25_promedio_24h / 10.0)) - 1) * 100, 2
            ) AS incremento_riesgo_pct_24h,
            -- Mantenemos incremento_riesgo_pct_actual por retrocompatibilidad
            ROUND(
                (EXP(ar.beta * (em.pm25_promedio_24h / 10.0)) - 1) * 100, 2
            ) AS incremento_riesgo_pct_actual,
            -- Propagación de incertidumbre estadística (IC 95%)
            ROUND(
                (POWER(ar.limite_inferior::numeric, (em.pm25_promedio_24h / 10.0)::numeric) - 1) * 100, 2
            ) AS incremento_riesgo_pct_inf,
            ROUND(
                (POWER(ar.limite_superior::numeric, (em.pm25_promedio_24h / 10.0)::numeric) - 1) * 100, 2
            ) AS incremento_riesgo_pct_sup
        FROM estacion_por_municipio em
        JOIN analisis_riesgo ar      ON ar.municipio_id = em.municipio_id
        JOIN grupos_diagnosticos gd  ON ar.grupo_diagnostico_id = gd.id
        JOIN contaminantes c         ON ar.contaminante_id = c.id
        WHERE c.nombre = 'pm25'
        ORDER BY em.municipio, ar.sexo, ar.grupo_edad;
        """

        cur.execute(sql_vista)
        conn.commit()
        print("[OK] Vista materializada 'vista_riesgo_integrado' creada/actualizada con promedio móvil 24 h.")
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Al crear/refrescar vista integrada: {e}")
        raise
    finally:
        cur.close()
