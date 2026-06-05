import sys
import os
import pandas as pd

# Añadir directorio actual al path por si se ejecuta desde carpetas superiores
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import MUNICIPIOS_MAPA
from limpieza_datos import limpiar_analisis_riesgo, limpiar_enfermedades, limpiar_tasa_mortalidad, limpiar_defunciones
from extract_siata import get_pm25_siata
import db_postgres

def ejecutar_pipeline_completo():
    """
    Orquestador Principal del Pipeline ETL.
    Corre en secuencia: Extracción -> Transformación -> Carga en PostgreSQL.
    """
    print("=" * 80)
    print("           INICIANDO PIPELINE ETL: CALIDAD DEL AIRE Y SALUD PÚBLICA")
    print("=" * 80)
    
    # 1. PASO: Asegurar base de datos y esquema de tablas relacionales
    try:
        db_postgres.crear_base_de_datos_si_no_existe()
        db_postgres.crear_esquema()
    except Exception as e:
        print(f"[ERROR] Error critico al inicializar la base de datos PostgreSQL: {e}")
        print("Asegurate de que el servidor PostgreSQL este corriendo localmente en el puerto 5432.")
        return False

        
    conn = db_postgres.get_connection()
    
    try:
        # 2. PASO: Cargar dimensiones fijas (contaminantes)
        db_postgres.poblar_dimensiones_basicas(conn)
        
        # 3. PASO: Carga de Datos Históricos (CSV) - Transformaciones de Compañeros
        print("\n--- Ejecutando Limpieza de Datos Históricos (Pandas) ---")
        df_riesgo = limpiar_analisis_riesgo()
        df_enfermedades = limpiar_enfermedades()
        df_mortalidad = limpiar_tasa_mortalidad()
        df_defunciones = limpiar_defunciones()
        
        # 4. PASO: Consolidar y poblar dinámicamente dimensiones compartidas
        print("\n--- Resolviendo Claves Foráneas y Catálogos ---")
        
        # Extraer municipios únicos de todos los sets de datos
        muns_riesgo = set(df_riesgo['municipio_normalizado'].dropna().unique())
        muns_enferm = set(df_enfermedades['municipio_normalizado'].dropna().unique())
        muns_mort = set(df_mortalidad['municipio_normalizado'].dropna().unique())
        muns_def = set(df_defunciones['municipio_normalizado'].dropna().unique())
        municipios_totales = list(muns_riesgo | muns_enferm | muns_mort | muns_def)
        
        # Extraer diagnósticos de enfermedades únicos
        diag_riesgo = set(df_riesgo['grupo_diagnostico'].dropna().unique())
        diag_enferm = set(df_enfermedades['grupo'].dropna().unique())
        diag_def = set(df_defunciones['grupo'].dropna().unique())
        diagnosticos_totales = list(diag_riesgo | diag_enferm | diag_def)
        
        # Asegurar dimensiones e IDs mapeados
        muns_id_map, diags_id_map = db_postgres.asegurar_municipios_y_diagnosticos(
            conn, municipios_totales, diagnosticos_totales
        )
        
        # 5. PASO: Cargar hechos históricos (vaciado y recarga limpia de CSVs)
        print("\n--- Cargando Hechos Históricos a PostgreSQL ---")
        db_postgres.vaciar_tablas_hechos(conn)
        
        db_postgres.cargar_analisis_riesgo(conn, df_riesgo, muns_id_map, diags_id_map)
        db_postgres.cargar_enfermedades(conn, df_enfermedades, muns_id_map, diags_id_map)
        db_postgres.cargar_tasa_mortalidad(conn, df_mortalidad, muns_id_map)
        db_postgres.cargar_defunciones(conn, df_defunciones, muns_id_map, diags_id_map)
        
        # 6. PASO: Datos en Tiempo Real (API SIATA)
        print("\n--- Cargando Datos de API SIATA (Tiempo Real) ---")
        df_siata = get_pm25_siata()
        db_postgres.cargar_mediciones_siata(conn, df_siata)
        
        # 7. PASO FINAL: Crear/Refrescar Vista Materializada Consolidada
        print("\n--- Consolidando Vista Integrada (3 fuentes combinadas) ---")
        db_postgres.crear_vista_datos_integrados(conn)
        
        print("\n" + "=" * 80)
        print("               ¡PIPELINE ETL EJECUTADO EXITOSAMENTE!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Ocurrio un error inesperado durante el pipeline: {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    ejecutar_pipeline_completo()
