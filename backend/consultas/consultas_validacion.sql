-- ============================================================================
-- CONSULTAS DE VALIDACIÓN - PIPELINE ETL
-- Materia: Integración y Adquisición de Datos
-- ============================================================================
-- Ejecuta estas consultas en tu herramienta de base de datos (pgAdmin, DBeaver, etc.)
-- para validar que todo el pipeline cargó los datos correctamente en PostgreSQL.

-- 1. CONTEO GENERAL DE REGISTROS POR TABLA
-- ----------------------------------------------------------------------------
SELECT 'municipios' AS tabla, COUNT(*) AS total FROM municipios
UNION ALL
SELECT 'contaminantes', COUNT(*) FROM contaminantes
UNION ALL
SELECT 'grupos_diagnosticos', COUNT(*) FROM grupos_diagnosticos
UNION ALL
SELECT 'analisis_riesgo', COUNT(*) FROM analisis_riesgo
UNION ALL
SELECT 'enfermedades', COUNT(*) FROM enfermedades
UNION ALL
SELECT 'tasa_mortalidad', COUNT(*) FROM tasa_mortalidad
UNION ALL
SELECT 'defunciones', COUNT(*) FROM defunciones
UNION ALL
SELECT 'mediciones_siata', COUNT(*) FROM mediciones_siata;


-- 2. VERIFICACIÓN DE CLAVES FORÁNEAS (INTEGRIDAD REFERENCIAL)
-- ----------------------------------------------------------------------------
-- ¿Hay registros en hechos que hagan referencia a un municipio inexistente?
SELECT COUNT(*) AS huerfanos_riesgo FROM analisis_riesgo WHERE municipio_id IS NULL;
SELECT COUNT(*) AS huerfanos_enfermedades FROM enfermedades WHERE municipio_id IS NULL;
SELECT COUNT(*) AS huerfanos_mortalidad FROM tasa_mortalidad WHERE municipio_id IS NULL;
SELECT COUNT(*) AS huerfanos_defunciones FROM defunciones WHERE municipio_id IS NULL;


-- 3. CONSULTA INTEGRADA: TOP 5 ENFERMEDADES CON MAYOR RIESGO POR CONTAMINANTE (PM2.5)
-- ----------------------------------------------------------------------------
SELECT 
    m.nombre_normalizado AS municipio,
    gd.nombre AS enfermedad,
    c.nombre_display AS contaminante,
    ar.grupo_edad,
    ar.sexo,
    ar.beta,
    ar.porcentaje_incremento_riesgo
FROM analisis_riesgo ar
JOIN municipios m ON ar.municipio_id = m.id
JOIN grupos_diagnosticos gd ON ar.grupo_diagnostico_id = gd.id
JOIN contaminantes c ON ar.contaminante_id = c.id
WHERE c.nombre = 'pm25'
ORDER BY ar.porcentaje_incremento_riesgo DESC
LIMIT 5;


-- 4. CONSULTA INTEGRADA: HISTÓRICO DE CASOS VS MEDICIÓN ACTUAL EN TIEM POREAL
-- ----------------------------------------------------------------------------
-- Muestra el promedio histórico de casos registrados por municipio al lado de la 
-- última lectura promedio de PM2.5 registrada por las estaciones de SIATA.
WITH prom_historico AS (
    SELECT 
        m.nombre_normalizado AS municipio,
        ROUND(AVG(e.casos), 2) AS promedio_casos_historico
    FROM enfermedades e
    JOIN municipios m ON e.municipio_id = m.id
    GROUP BY m.nombre_normalizado
),
siata_actual AS (
    -- Asumimos que podemos asociar estaciones a municipios por coincidencia de nombre en el texto
    -- o simplemente calcular el promedio regional actual.
    SELECT 
        ROUND(AVG(pm25_ica), 2) AS promedio_pm25_actual
    FROM mediciones_siata
    WHERE pm25_ica IS NOT NULL
)
SELECT 
    ph.municipio,
    ph.promedio_casos_historico,
    (SELECT promedio_pm25_actual FROM siata_actual) AS pm25_promedio_valle_aburra
FROM prom_historico ph
ORDER BY ph.promedio_casos_historico DESC;


-- 5. MONITOREO DE MEDICIONES SIATA EN TIEMPO REAL
-- ----------------------------------------------------------------------------
-- Muestra las últimas 10 mediciones recibidas por el scheduler.
SELECT 
    estacion,
    pm25_ica,
    categoria_ica,
    fecha_hora,
    fecha_carga
FROM mediciones_siata
ORDER BY fecha_carga DESC, pm25_ica DESC
LIMIT 10;
