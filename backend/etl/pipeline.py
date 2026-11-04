"""
Orquestador Principal del Pipeline ETL
========================================
Ejecuta en secuencia las 3 fases de la metodología:

    FASE 1 — EXTRACCIÓN:
        Extrae datos de 5 fuentes heterogéneas (4 CSVs + 1 API en tiempo real)

    FASE 2 — TRANSFORMACIÓN:
        Limpia, normaliza y valida los datos de cada fuente

    FASE 3 — INTEGRACIÓN Y CARGA:
        Carga en PostgreSQL y crea la vista materializada que unifica las 3 fuentes

Reproducibilidad (respuesta a evaluadores)
-------------------------------------------
    Lenguaje:      Python 3.8+
    Librerías:     pandas, requests, psycopg2, schedule (ver requirements.txt)
    Base de datos: PostgreSQL 14+ (local o Neon.tech en nube)
    API SIATA:     https://www.siata.gov.co/kml/01_Redes/AMVARedAire/RedAireAMVA_PM25.kml
    Frecuencia:    Ejecución única para históricos + scheduler para SIATA
    Idempotencia:  TRUNCATE + INSERT para históricos, UPSERT para SIATA

Ejecución
---------
    Desde la carpeta backend/:
        python -m etl.pipeline
"""

import sys
import os

# Asegurar que backend/ esté en el path para imports absolutos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Fase 1: Extracción ────────────────────────────────────────────────────
from etl.extraccion.siata_api import extraer_siata

# ── Fase 2: Transformación ────────────────────────────────────────────────
from etl.transformacion.limpieza_riesgo import limpiar_analisis_riesgo
from etl.transformacion.limpieza_enfermedades import limpiar_enfermedades
from etl.transformacion.limpieza_mortalidad import limpiar_tasa_mortalidad
from etl.transformacion.limpieza_defunciones import limpiar_defunciones
from etl.transformacion.calidad_datos import validar_calidad_datos

# ── Fase 3: Carga e Integración ───────────────────────────────────────────
from etl.carga.conexion import get_connection, crear_base_de_datos_si_no_existe
from etl.carga.esquema import crear_esquema
from etl.carga.dimensiones import poblar_dimensiones_basicas, asegurar_municipios_y_diagnosticos
from etl.carga.hechos import (
    vaciar_tablas_hechos,
    cargar_analisis_riesgo,
    cargar_enfermedades,
    cargar_tasa_mortalidad,
    cargar_defunciones,
)
from etl.carga.siata import cargar_mediciones_siata
from etl.transformacion.asignacion_municipio import asignar_municipio
from etl.carga.vista_integrada import crear_vista_datos_integrados


def ejecutar_pipeline_completo():
    """
    Orquestador Principal del Pipeline ETL.
    Corre en secuencia: Extracción → Transformación → Carga en PostgreSQL.

    Returns:
        bool: True si el pipeline se ejecutó exitosamente, False en caso de error.
    """
    print("=" * 80)
    print("       PIPELINE ETL: CALIDAD DEL AIRE Y SALUD PÚBLICA")
    print("       Valle de Aburrá — 10 municipios del AMVA")
    print("=" * 80)

    # ══════════════════════════════════════════════════════════════════════
    # PASO 0: Preparar la base de datos
    # ══════════════════════════════════════════════════════════════════════
    try:
        crear_base_de_datos_si_no_existe()
        crear_esquema()
    except Exception as e:
        print(f"[ERROR] Error crítico al inicializar PostgreSQL: {e}")
        print("Asegúrate de que el servidor PostgreSQL esté corriendo.")
        return False

    conn = get_connection()

    try:
        # ══════════════════════════════════════════════════════════════════
        # FASE 1: EXTRACCIÓN — Identificación de fuentes
        # ══════════════════════════════════════════════════════════════════
        print("\n" + "─" * 80)
        print("  FASE 1: EXTRACCIÓN — Cargando fuentes de datos")
        print("─" * 80)

        # Cargar dimensiones fijas (contaminantes: PM10, PM2.5, O3)
        poblar_dimensiones_basicas(conn)

        # ══════════════════════════════════════════════════════════════════
        # FASE 2: TRANSFORMACIÓN — Limpieza y normalización
        # ══════════════════════════════════════════════════════════════════
        print("\n" + "─" * 80)
        print("  FASE 2: TRANSFORMACIÓN — Limpieza de datos históricos")
        print("─" * 80)

        df_riesgo       = limpiar_analisis_riesgo()
        df_enfermedades = limpiar_enfermedades()
        df_mortalidad   = limpiar_tasa_mortalidad()
        df_defunciones  = limpiar_defunciones()

        # Validación de calidad de datos (respuesta a evaluadores)
        print("\n" + "─" * 80)
        print("  VALIDACIÓN DE CALIDAD DE DATOS")
        print("─" * 80)
        validar_calidad_datos(df_riesgo, "AnalisisRiesgo (PM2.5)")
        validar_calidad_datos(df_enfermedades, "Enfermedades (2008-2017)")
        validar_calidad_datos(df_mortalidad, "Tasa de Mortalidad")
        validar_calidad_datos(df_defunciones, "Defunciones")

        # ══════════════════════════════════════════════════════════════════
        # FASE 3: CARGA E INTEGRACIÓN — Almacenamiento en PostgreSQL
        # ══════════════════════════════════════════════════════════════════
        print("\n" + "─" * 80)
        print("  FASE 3: CARGA E INTEGRACIÓN — PostgreSQL")
        print("─" * 80)

        # ── 3.1 Consolidar y poblar dimensiones compartidas ────────────
        print("\n--- Resolviendo claves foráneas y catálogos ---")

        # Extraer municipios únicos de los 4 datasets
        muns_riesgo  = set(df_riesgo['municipio_normalizado'].dropna().unique())
        muns_enferm  = set(df_enfermedades['municipio_normalizado'].dropna().unique())
        muns_mort    = set(df_mortalidad['municipio_normalizado'].dropna().unique())
        muns_def     = set(df_defunciones['municipio_normalizado'].dropna().unique())
        municipios_totales = list(muns_riesgo | muns_enferm | muns_mort | muns_def)

        # Extraer diagnósticos únicos
        diag_riesgo  = set(df_riesgo['grupo_diagnostico'].dropna().unique())
        diag_enferm  = set(df_enfermedades['grupo'].dropna().unique())
        diag_def     = set(df_defunciones['grupo'].dropna().unique())
        diagnosticos_totales = list(diag_riesgo | diag_enferm | diag_def)

        # Asegurar dimensiones e IDs mapeados
        muns_id_map, diags_id_map = asegurar_municipios_y_diagnosticos(
            conn, municipios_totales, diagnosticos_totales
        )

        # ── 3.2 Cargar hechos históricos (TRUNCATE + INSERT) ──────────
        print("\n--- Cargando hechos históricos a PostgreSQL ---")
        vaciar_tablas_hechos(conn)

        cargar_analisis_riesgo(conn, df_riesgo, muns_id_map, diags_id_map)
        cargar_enfermedades(conn, df_enfermedades, muns_id_map, diags_id_map)
        cargar_tasa_mortalidad(conn, df_mortalidad, muns_id_map)
        cargar_defunciones(conn, df_defunciones, muns_id_map, diags_id_map)

        # ── 3.3 Datos en tiempo real (API SIATA con UPSERT) ───────────
        print("\n--- Cargando datos de API SIATA (Tiempo Real) ---")
        df_siata = extraer_siata()
        # Asignar municipio de forma robusta (fallback geográfico)
        df_siata = asignar_municipio(df_siata)
        cargar_mediciones_siata(conn, df_siata)

        # ── 3.4 Crear/Refrescar vista materializada de integración ─────
        print("\n--- Consolidando vista integrada (3 fuentes combinadas) ---")
        crear_vista_datos_integrados(conn)

        print("\n" + "=" * 80)
        print("       ¡PIPELINE ETL EJECUTADO EXITOSAMENTE!")
        print("=" * 80)
        return True

    except Exception as e:
        print(f"\n[ERROR] Error inesperado durante el pipeline: {e}")
        return False
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Punto de entrada: python -m etl.pipeline
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    ejecutar_pipeline_completo()
