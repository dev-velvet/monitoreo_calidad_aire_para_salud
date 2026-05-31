from fastapi import APIRouter, Query
from app.database import get_db

router = APIRouter(prefix="/api/siata", tags=["siata"])

@router.get("/actual")
def get_siata_actual():
    """
    Retorna la última medición disponible para cada estación SIATA de PM2.5.
    Usa DISTINCT ON para asegurar una única fila por estación (la más reciente).
    """
    query = """
        SELECT DISTINCT ON (estacion)
            id, estacion, pm25_ica, fecha_hora, latitud, longitud, categoria_ica, fecha_carga
        FROM mediciones_siata
        ORDER BY estacion, fecha_hora DESC;
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

@router.get("/promedio")
def get_siata_promedio():
    """
    Calcula el promedio general de PM2.5 en la región (Valle de Aburrá) 
    y reporta la estación con la lectura más alta en vivo.
    """
    query_promedio = """
        WITH ultimas_mediciones AS (
            SELECT DISTINCT ON (estacion) pm25_ica
            FROM mediciones_siata
            WHERE pm25_ica IS NOT NULL
            ORDER BY estacion, fecha_hora DESC
        )
        SELECT ROUND(AVG(pm25_ica), 2) as promedio_region FROM ultimas_mediciones;
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
            promedio = res_prom["promedio_region"] if res_prom else None
            
            cur.execute(query_maximo)
            estaciones = cur.fetchall()
            
            peor_estacion = None
            if estaciones:
                # Ordenar en python para obtener la de mayor pm25
                estaciones_ordenadas = sorted(estaciones, key=lambda x: x["pm25_ica"], reverse=True)
                peor_estacion = estaciones_ordenadas[0]
                
            return {
                "promedio_valle_aburra": promedio,
                "peor_estacion": peor_estacion
            }
