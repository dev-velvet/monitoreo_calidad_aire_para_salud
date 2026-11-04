from fastapi import APIRouter, Query
from app.database import get_db

router = APIRouter(prefix="/api/siata", tags=["siata"])

@router.get("/actual")
def get_siata_actual():
    """
    Retorna la última medición disponible para cada estación SIATA de PM2.5,
    junto con su promedio móvil de las últimas 24 horas y el número de lecturas.
    """
    query = """
        WITH ultimas AS (
            SELECT DISTINCT ON (estacion)
                id, estacion, pm25_ica, fecha_hora, latitud, longitud, categoria_ica, fecha_carga
            FROM mediciones_siata
            WHERE pm25_ica IS NOT NULL
            ORDER BY estacion, fecha_hora DESC
        ),
        promedios_24h AS (
            SELECT
                estacion,
                ROUND(AVG(pm25_ica)::numeric, 2) AS pm25_promedio_24h,
                COUNT(pm25_ica) AS n_lecturas_24h
            FROM mediciones_siata
            WHERE pm25_ica IS NOT NULL AND pm25_ica >= 0
              AND fecha_hora >= (
                  SELECT COALESCE(MAX(fecha_hora) - INTERVAL '24 hours', NOW() - INTERVAL '24 hours')
                  FROM mediciones_siata
              )
            GROUP BY estacion
        )
        SELECT 
            u.id, 
            u.estacion, 
            u.pm25_ica, 
            COALESCE(p.pm25_promedio_24h, u.pm25_ica) AS pm25_promedio_24h,
            COALESCE(p.n_lecturas_24h, 1) AS n_lecturas_24h,
            u.fecha_hora, 
            u.latitud, 
            u.longitud, 
            u.categoria_ica AS categoria_ica_actual,
            CASE
                WHEN COALESCE(p.pm25_promedio_24h, u.pm25_ica) <= 12 THEN 'Buena'
                WHEN COALESCE(p.pm25_promedio_24h, u.pm25_ica) <= 37 THEN 'Moderada'
                WHEN COALESCE(p.pm25_promedio_24h, u.pm25_ica) <= 55 THEN 'Dañina a grupos sensibles'
                WHEN COALESCE(p.pm25_promedio_24h, u.pm25_ica) <= 150 THEN 'Dañina'
                WHEN COALESCE(p.pm25_promedio_24h, u.pm25_ica) <= 250 THEN 'Muy dañina'
                ELSE 'Peligrosa'
            END AS categoria_ica_24h,
            u.categoria_ica, 
            u.fecha_carga
        FROM ultimas u
        LEFT JOIN promedios_24h p ON u.estacion = p.estacion
        ORDER BY u.estacion;
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

@router.get("/promedio")
def get_siata_promedio():
    """
    Calcula el promedio general de PM2.5 en la región (Valle de Aburrá)
    tanto en ventana móvil de 24 horas como en tiempo real instantáneo,
    y reporta la estación con la lectura más alta.
    """
    query_promedio = """
        WITH ventana_24h AS (
            SELECT pm25_ica
            FROM mediciones_siata
            WHERE pm25_ica IS NOT NULL AND pm25_ica >= 0
              AND fecha_hora >= (
                  SELECT COALESCE(MAX(fecha_hora) - INTERVAL '24 hours', NOW() - INTERVAL '24 hours')
                  FROM mediciones_siata
              )
        ),
        ultimas_mediciones AS (
            SELECT DISTINCT ON (estacion) pm25_ica
            FROM mediciones_siata
            WHERE pm25_ica IS NOT NULL
            ORDER BY estacion, fecha_hora DESC
        )
        SELECT 
            ROUND(AVG(u.pm25_ica)::numeric, 2) as promedio_region_actual,
            ROUND(AVG(v.pm25_ica)::numeric, 2) as promedio_region_24h
        FROM ultimas_mediciones u
        CROSS JOIN (SELECT AVG(pm25_ica) as pm25_ica FROM ventana_24h) v;
    """
    query_maximo = """
        SELECT DISTINCT ON (estacion) estacion, pm25_ica, categoria_ica
        FROM mediciones_siata
        WHERE pm25_ica IS NOT NULL
        ORDER BY estacion, fecha_hora DESC
    """
    
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query_promedio)
            res_prom = cur.fetchone()
            promedio_act = res_prom["promedio_region_actual"] if res_prom else None
            promedio_24h = res_prom["promedio_region_24h"] if res_prom and res_prom.get("promedio_region_24h") is not None else promedio_act
            
            cur.execute(query_maximo)
            estaciones = cur.fetchall()
            
            peor_estacion = None
            if estaciones:
                # Ordenar en python para obtener la de mayor pm25
                estaciones_ordenadas = sorted(estaciones, key=lambda x: x["pm25_ica"], reverse=True)
                peor_estacion = estaciones_ordenadas[0]
                
            return {
                "promedio_valle_aburra": promedio_24h,
                "promedio_valle_aburra_24h": promedio_24h,
                "promedio_valle_aburra_instantaneo": promedio_act,
                "peor_estacion": peor_estacion
            }
