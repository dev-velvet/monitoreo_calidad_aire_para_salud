from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.database import get_db
from etl.extraccion.siata_api import _clasificar_ica as clasificar_ica_pm25

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
        
    query += " ORDER BY e.periodo ASC, e.casos DESC;"
    
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
        
    query += " ORDER BY d.periodo ASC;"
    
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
    Garantiza que cualquier combinación de parámetros retorne una estimación válida,
    aplicando fallbacks inteligentes y explicando las adaptaciones en 'nota_estimacion'.
    """
    import math

    with get_db() as conn:
        with conn.cursor() as cur:
            # 1. Obtener nombre del municipio solicitado
            cur.execute("SELECT nombre_normalizado FROM municipios WHERE id = %s;", (municipio_id,))
            mun_res = cur.fetchone()
            if not mun_res:
                raise HTTPException(status_code=404, detail="Municipio no encontrado")
            nombre_muni = mun_res["nombre_normalizado"]

            # 2. Encontrar el ID de Medellín como proxy de referencia
            cur.execute("SELECT id FROM municipios WHERE nombre_normalizado ILIKE '%Medell%' LIMIT 1;")
            medellin_res = cur.fetchone()
            medellin_id = medellin_res["id"] if medellin_res else 1

            # 3. Normalizar sexo
            sexo_normalizado = "Ambos sexos"
            if sexo:
                sex_lower = sexo.lower()
                if "homb" in sex_lower or "masc" in sex_lower or sex_lower == "m":
                    sexo_normalizado = "Hombre"
                elif "muj" in sex_lower or "fem" in sex_lower or sex_lower == "f":
                    sexo_normalizado = "Mujer"

            # 4. Normalizar grupo de edad (DB tiene: '5 a 14 años', 'Mayores de 65 años', 'Menores de 5 años')
            grupo_edad_normalizado = "Mayores de 65 años"  # Default/Adult proxy
            if grupo_edad:
                ge_lower = grupo_edad.lower()
                if "menor" in ge_lower or "bajo 5" in ge_lower or "<5" in ge_lower:
                    grupo_edad_normalizado = "Menores de 5 años"
                elif "5 a 14" in ge_lower or "5-14" in ge_lower:
                    grupo_edad_normalizado = "5 a 14 años"

            # 5. Obtener medición de PM2.5 del municipio
            cur.execute("""
                SELECT pm25_actual, categoria_ica, estacion_siata
                FROM vista_riesgo_integrado 
                WHERE municipio_id = %s 
                LIMIT 1;
            """, (municipio_id,))
            medicion_res = cur.fetchone()
            
            nota_muni = None
            if medicion_res:
                estacion_siata = medicion_res["estacion_siata"]
                pm25_actual = float(medicion_res["pm25_actual"])
                categoria_ica = medicion_res["categoria_ica"]
            else:
                # Fallback: Promedio regional de todas las estaciones activas
                cur.execute("""
                    WITH ultimas AS (
                        SELECT DISTINCT ON (estacion) pm25_ica
                        FROM mediciones_siata
                        WHERE pm25_ica IS NOT NULL
                        ORDER BY estacion, fecha_hora DESC
                    )
                    SELECT AVG(pm25_ica) as promedio FROM ultimas;
                """)
                fallback_res = cur.fetchone()
                pm25_actual = float(fallback_res["promedio"]) if fallback_res and fallback_res["promedio"] else 0.0
                categoria_ica = clasificar_ica_pm25(pm25_actual)
                estacion_siata = "Promedio Regional (Valle de Aburrá)"
                nota_muni = f"No hay estaciones de monitoreo activas en {nombre_muni}. Se utiliza el promedio regional."

            # 6. Obtener coeficientes de riesgo (beta)
            # Primero intentamos con el municipio solicitado, sexo y grupo edad normalizados
            cur.execute("""
                SELECT gd.nombre as enfermedad, ar.beta, ar.porcentaje_incremento_riesgo
                FROM analisis_riesgo ar
                JOIN grupos_diagnosticos gd ON ar.grupo_diagnostico_id = gd.id
                WHERE ar.municipio_id = %s 
                  AND ar.sexo ILIKE %s
                  AND ar.grupo_edad ILIKE %s;
            """, (municipio_id, sexo_normalizado, grupo_edad_normalizado))
            filas_coef = cur.fetchall()
            
            nota_coef = None
            
            # Si no hay datos, probar con Medellín (municipio de referencia)
            if not filas_coef:
                cur.execute("""
                    SELECT gd.nombre as enfermedad, ar.beta, ar.porcentaje_incremento_riesgo
                    FROM analisis_riesgo ar
                    JOIN grupos_diagnosticos gd ON ar.grupo_diagnostico_id = gd.id
                    WHERE ar.municipio_id = %s 
                      AND ar.sexo ILIKE %s
                      AND ar.grupo_edad ILIKE %s;
                """, (medellin_id, sexo_normalizado, grupo_edad_normalizado))
                filas_coef = cur.fetchall()
                if filas_coef:
                    nota_coef = f"Se utilizan coeficientes de Medellín como referencia para {nombre_muni}."
            
            # Si todavía no hay datos, probar con 'Ambos sexos' y 'Mayores de 65 años' en Medellín
            if not filas_coef:
                cur.execute("""
                    SELECT gd.nombre as enfermedad, ar.beta, ar.porcentaje_incremento_riesgo
                    FROM analisis_riesgo ar
                    JOIN grupos_diagnosticos gd ON ar.grupo_diagnostico_id = gd.id
                    WHERE ar.municipio_id = %s 
                      AND ar.sexo = 'Ambos sexos'
                      AND ar.grupo_edad = 'Mayores de 65 años';
                """, (medellin_id,))
                filas_coef = cur.fetchall()
                if filas_coef:
                    nota_coef = f"Se utilizan coeficientes genéricos de referencia para {nombre_muni}."

            # 7. Calcular los incrementos de riesgo para cada enfermedad usando el PM2.5 real/promedio
            calculos = []
            for f in filas_coef:
                beta = float(f["beta"])
                # Fórmula estándar epidemiológica: incremento por cada incremento en PM2.5 (per-10µg/m³)
                inc_pct = round((math.exp(beta * (pm25_actual / 10.0)) - 1) * 100, 2)
                calculos.append({
                    "enfermedad": f["enfermedad"],
                    "beta_historico": beta,
                    "incremento_riesgo_porcentaje_actual": inc_pct,
                    "incremento_historico_base": float(f["porcentaje_incremento_riesgo"])
                })

            # Ordenar los resultados de mayor a menor riesgo incremental
            calculos.sort(key=lambda x: x["incremento_riesgo_porcentaje_actual"], reverse=True)

            # Compilar nota explicativa
            notas = [n for n in [nota_muni, nota_coef] if n]
            if grupo_edad != grupo_edad_normalizado:
                # Si el usuario ingresó un grupo de edad para el que no tenemos coeficientes (ej. 15-64)
                # se le avisa que se usó el grupo de referencia (ej. Mayores de 65 años)
                notas.append(f"Estimación adaptada usando el grupo etario '{grupo_edad_normalizado}' (referencia de adultos).")
            
            nota_estimacion = " | ".join(notas) if notas else "Estimación personalizada basada en datos locales y coeficientes epidemiológicos."

            return {
                "municipio": nombre_muni,
                "estacion_monitoreo": estacion_siata,
                "pm25_ica_actual": pm25_actual,
                "categoria_ica": categoria_ica,
                "sexo_filtro": sexo,
                "grupo_edad_filtro": grupo_edad,
                "calculos_riesgo": calculos,
                "nota_estimacion": nota_estimacion
            }

