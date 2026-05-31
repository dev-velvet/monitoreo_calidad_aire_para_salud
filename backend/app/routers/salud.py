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
    Busca la estación de SIATA correspondiente al municipio dado, obtiene su PM2.5 actual
    y calcula el incremento de riesgo relativo con el coeficiente beta histórico.
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            # 1. Obtener el nombre normalizado del municipio
            cur.execute("SELECT nombre_normalizado FROM municipios WHERE id = %s;", (municipio_id,))
            mun_res = cur.fetchone()
            if not mun_res:
                raise HTTPException(status_code=404, detail="Municipio no encontrado")
            
            municipio_nombre = mun_res["nombre_normalizado"]
            
            # 2. Buscar la estación SIATA correspondiente al municipio (coincidencia parcial de texto)
            # Ej: Estación Sabaneta - I.E. Rafael J. Mejía -> LIKE '%Sabaneta%'
            query_siata = """
                SELECT DISTINCT ON (estacion) pm25_ica, estacion, categoria_ica
                FROM mediciones_siata
                WHERE estacion ILIKE %s AND pm25_ica IS NOT NULL
                ORDER BY estacion, fecha_hora DESC;
            """
            cur.execute(query_siata, (f"%{municipio_nombre}%",))
            siata_res = cur.fetchone()
            
            if not siata_res:
                # Si no hay estación exacta en ese municipio, tomamos el promedio regional como fallback
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
                pm25_actual = float(fallback_res["promedio"]) if fallback_res and fallback_res["promedio"] else 0.0
                estacion_usada = "Promedio Regional (Valle de Aburrá)"
                categoria_ica = "Moderada" if pm25_actual > 12 else "Buena"
            else:
                pm25_actual = float(siata_res["pm25_ica"])
                estacion_usada = siata_res["estacion"]
                categoria_ica = siata_res["categoria_ica"]
                
            # 3. Consultar coeficientes Beta para el municipio, sexo y grupo de edad especificados
            query_beta = """
                SELECT 
                    gd.nombre as enfermedad, ar.beta, ar.porcentaje_incremento_riesgo as incremento_basico_historico
                FROM analisis_riesgo ar
                JOIN grupos_diagnosticos gd ON ar.grupo_diagnostico_id = gd.id
                JOIN contaminantes c ON ar.contaminante_id = c.id
                WHERE ar.municipio_id = %s 
                  AND ar.sexo ILIKE %s 
                  AND ar.grupo_edad ILIKE %s
                  AND c.nombre = 'pm25';
            """
            cur.execute(query_beta, (municipio_id, sexo, grupo_edad))
            betas = cur.fetchall()
            
            # 4. Calcular el incremento de riesgo personalizado en tiempo real
            # Formula: Incremento % = (e^(beta * PM25) - 1) * 100
            import math
            calculos = []
            for b in betas:
                beta_val = float(b["beta"])
                # Incremento de riesgo relativo según la exposición actual
                incremento_real = (math.exp(beta_val * pm25_actual) - 1) * 100
                calculos.append({
                    "enfermedad": b["enfermedad"],
                    "beta_historico": beta_val,
                    "incremento_riesgo_porcentaje_actual": round(incremento_real, 2),
                    "incremento_historico_base": float(b["incremento_basico_historico"])
                })
                
            return {
                "municipio": municipio_nombre,
                "estacion_monitoreo": estacion_usada,
                "pm25_ica_actual": pm25_actual,
                "categoria_ica": categoria_ica,
                "sexo_filtro": sexo,
                "grupo_edad_filtro": grupo_edad,
                "calculos_riesgo": calculos
            }
