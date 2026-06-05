from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.database import get_db

router = APIRouter(prefix="/api/salud", tags=["salud"])

@router.get("/riesgo")
def get_riesgo(
    municipio_id: Optional[int] = None,
    sexo: Optional[str] = None,
    grupo_edad: Optional[str] = None
):
    """
    Consulta los coeficientes beta de riesgo epidemiológico histórico.
    """
    query = """
        SELECT 
            ar.id, m.nombre_normalizado as municipio, gd.nombre as grupo_diagnostico,
            c.nombre_display as contaminante, ar.tipo_rezago, ar.sexo, ar.grupo_edad,
            ar.beta, ar.exponencial_beta, ar.porcentaje_incremento_riesgo
        FROM analisis_riesgo ar
        JOIN municipios m ON ar.municipio_id = m.id
        JOIN grupos_diagnosticos gd ON ar.grupo_diagnostico_id = gd.id
        JOIN contaminantes c ON ar.contaminante_id = c.id
        WHERE 1=1
    """
    params = []
    if municipio_id:
        query += " AND ar.municipio_id = %s"
        params.append(municipio_id)
    if sexo:
        query += " AND ar.sexo ILIKE %s"
        params.append(sexo)
    if grupo_edad:
        query += " AND ar.grupo_edad ILIKE %s"
        params.append(grupo_edad)
        
    query += " ORDER BY ar.porcentaje_incremento_riesgo DESC LIMIT 100;"
    
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

@router.get("/historico/enfermedades")
def get_historico_enfermedades(
    municipio_id: Optional[int] = None,
    grupo_diagnostico_id: Optional[int] = None,
    sexo: Optional[str] = None,
    grupo_edad: Optional[str] = None
):
    """
    Retorna la serie temporal histórica de casos de enfermedades respiratorias.
    """
    query = """
        SELECT 
            e.periodo as anio, m.nombre_normalizado as municipio, gd.nombre as grupo_diagnostico,
            e.sexo, e.grupo_edad, e.casos
        FROM enfermedades e
        JOIN municipios m ON e.municipio_id = m.id
        JOIN grupos_diagnosticos gd ON e.grupo_diagnostico_id = gd.id
        WHERE 1=1
    """
    params = []
    if municipio_id:
        query += " AND e.municipio_id = %s"
        params.append(municipio_id)
    if grupo_diagnostico_id:
        query += " AND e.grupo_diagnostico_id = %s"
        params.append(grupo_diagnostico_id)
    if sexo:
        query += " AND e.sexo ILIKE %s"
        params.append(sexo)
    if grupo_edad:
        query += " AND e.grupo_edad ILIKE %s"
        params.append(grupo_edad)
        
    query += " ORDER BY e.periodo ASC, e.casos DESC LIMIT 500;"
    
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

@router.get("/historico/defunciones")
def get_historico_defunciones(
    municipio_id: Optional[int] = None,
    grupo_diagnostico_id: Optional[int] = None
):
    """
    Retorna las defunciones registradas históricamente por municipio y grupo diagnóstico.
    """
    query = """
        SELECT 
            d.periodo as anio, m.nombre_normalizado as municipio, gd.nombre as grupo_diagnostico,
            d.sexo, d.grupo_edad, d.muertes
        FROM defunciones d
        JOIN municipios m ON d.municipio_id = m.id
        JOIN grupos_diagnosticos gd ON d.grupo_diagnostico_id = gd.id
        WHERE 1=1
    """
    params = []
    if municipio_id:
        query += " AND d.municipio_id = %s"
        params.append(municipio_id)
    if grupo_diagnostico_id:
        query += " AND d.grupo_diagnostico_id = %s"
        params.append(grupo_diagnostico_id)
        
    query += " ORDER BY d.periodo ASC LIMIT 500;"
    
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

@router.get("/riesgo-cruzado")
def get_riesgo_cruzado(
    municipio_id: int,
    sexo: Optional[str] = "Ambos",
    grupo_edad: Optional[str] = "65 años y más"
):
    """
    Calculadora de Riesgo Epidemiológico Cruzado en Tiempo Real (Diferenciador).
    Consulta la vista materializada 'vista_riesgo_integrado' que consolida
    las tres fuentes (SIATA en vivo + riesgo histórico + enfermedades).
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT municipio, estacion_siata, pm25_actual, categoria_ica,
                       ultima_medicion, enfermedad, coeficiente_riesgo,
                       incremento_basico_historico, incremento_riesgo_pct_actual
                FROM vista_riesgo_integrado
                WHERE municipio_id = %s
                  AND sexo ILIKE %s
                  AND grupo_edad ILIKE %s
                ORDER BY incremento_riesgo_pct_actual DESC;
            """
            cur.execute(query, (municipio_id, sexo, grupo_edad))
            filas = cur.fetchall()

            if not filas:
                # Fallback: promedio regional si no hay datos en la vista
                query_fallback = """
                    WITH ultimas AS (
                        SELECT DISTINCT ON (estacion) pm25_ica
                        FROM mediciones_siata
                        WHERE pm25_ica IS NOT NULL
                        ORDER BY estacion, fecha_hora DESC
                    )
                    SELECT AVG(pm25_ica) as promedio FROM ultimas;
                """
                cur.execute(query_fallback)
                fallback_res = cur.fetchone()
                pm25_fallback = float(fallback_res["promedio"]) if fallback_res and fallback_res["promedio"] else 0.0

                cur.execute("SELECT nombre_normalizado FROM municipios WHERE id = %s;", (municipio_id,))
                mun_res = cur.fetchone()
                if not mun_res:
                    raise HTTPException(status_code=404, detail="Municipio no encontrado")

                return {
                    "municipio": mun_res["nombre_normalizado"],
                    "estacion_monitoreo": "Promedio Regional (Valle de Aburrá)",
                    "pm25_ica_actual": pm25_fallback,
                    "categoria_ica": "Moderada" if pm25_fallback > 12 else "Buena",
                    "sexo_filtro": sexo,
                    "grupo_edad_filtro": grupo_edad,
                    "calculos_riesgo": []
                }

            primera = filas[0]
            calculos = [
                {
                    "enfermedad": f["enfermedad"],
                    "beta_historico": float(f["coeficiente_riesgo"]),
                    "incremento_riesgo_porcentaje_actual": float(f["incremento_riesgo_pct_actual"]),
                    "incremento_historico_base": float(f["incremento_basico_historico"])
                }
                for f in filas
            ]

            return {
                "municipio": primera["municipio"],
                "estacion_monitoreo": primera["estacion_siata"],
                "pm25_ica_actual": float(primera["pm25_actual"]),
                "categoria_ica": primera["categoria_ica"],
                "sexo_filtro": sexo,
                "grupo_edad_filtro": grupo_edad,
                "calculos_riesgo": calculos
            }
