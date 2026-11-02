"""
Limpieza de Datos — AnalisisRiesgo_20082017.csv
================================================
Carga y transforma el dataset de análisis de riesgo epidemiológico
proveniente del portal de datos abiertos del AMVA.

Contenido del dataset
---------------------
    - 1,652 registros (después de filtrar por PM2.5)
    - Coeficientes beta (β) de modelos de regresión que cuantifican
      la relación entre PM2.5 y enfermedades respiratorias
    - Desagregado por: municipio, sexo, grupo de edad, diagnóstico CIE-10

Importancia para la investigación
----------------------------------
    Los coeficientes β son el CORAZÓN del cálculo de riesgo:
        ΔR = (e^(β × PM2.5_actual / 10) − 1) × 100

    Esta fórmula estima el incremento porcentual del riesgo epidemiológico
    a partir de la concentración de PM2.5 medida en tiempo real.

Transformaciones aplicadas
--------------------------
    1. Filtro por contaminante PM2.5 (se descartan PM10 y O3)
    2. Limpieza de textos: strip() en columnas categóricas
    3. Corrección de decimales: comas → puntos en columnas numéricas
    4. Eliminación de registros duplicados
    5. Normalización Min-Max de columnas numéricas (para visualización)
    6. Normalización de nombres de municipio y grupos de edad
    7. Renombrado de columnas a snake_case para PostgreSQL
"""

import pandas as pd

from etl.configuracion.settings import CSV_ANALISIS_RIESGO
from etl.configuracion.diccionarios import MUNICIPIOS_MAPA, EDADES_MAPA


def limpiar_analisis_riesgo():
    """
    Carga y limpia el archivo AnalisisRiesgo_20082017.csv.

    Returns:
        pd.DataFrame limpio con columnas normalizadas listas para PostgreSQL.
    """
    print(f"-> Cargando y limpiando Análisis de Riesgo desde: {CSV_ANALISIS_RIESGO}")
    df = pd.read_csv(CSV_ANALISIS_RIESGO, sep=';', encoding='utf-8-sig')

    # ── 1. Filtrar solo registros de PM2.5 ─────────────────────────────────
    df = df[df['nombre contaminante'] == 'pm25'].reset_index(drop=True)
    print(f'   Filas después del filtro PM2.5: {len(df)}')

    df_limpio = df.copy()

    # ── 2. Limpieza de textos ──────────────────────────────────────────────
    cols_text = [
        'tipo de rezago', 'municipio', 'grupo diagnóstico',
        'nombre contaminante', 'sexo', 'edad', 'rezago'
    ]
    for col in cols_text:
        df_limpio[col] = df_limpio[col].astype(str).str.strip()

    # ── 3. Corrección de decimales: comas → puntos ─────────────────────────
    cols_num = [
        'beta del contaminante',
        'exponencial del beta',
        'limite inferior del exponencial del beta',
        'limite superior del exponencial del beta',
        'porcentaje del incremento del riesgo'
    ]
    for col in cols_num:
        df_limpio[col] = (
            df_limpio[col].astype(str)
            .str.replace(',', '.', regex=False)
            .astype(float)
        )

    # ── 4. Eliminación de duplicados ───────────────────────────────────────
    duplicadas = df_limpio.duplicated().sum()
    print(f'   Filas duplicadas eliminadas: {duplicadas}')
    df_limpio = df_limpio.drop_duplicates()

    # ── 5. Normalización Min-Max (para visualización, no para BD) ──────────
    for col in cols_num:
        min_val = df_limpio[col].min()
        max_val = df_limpio[col].max()
        if max_val != min_val:
            df_limpio[col + '_normalizado'] = (df_limpio[col] - min_val) / (max_val - min_val)
        else:
            df_limpio[col + '_normalizado'] = 0.0

    # ── 6. Normalización de municipios y grupos de edad ────────────────────
    df_limpio['municipio_normalizado'] = (
        df_limpio['municipio'].str.lower().str.strip()
        .map(MUNICIPIOS_MAPA)
        .fillna(df_limpio['municipio'])
    )
    df_limpio['grupo_edad_normalizado'] = (
        df_limpio['edad'].str.lower().str.strip()
        .map(EDADES_MAPA)
        .fillna(df_limpio['edad'])
    )

    # ── 7. Renombrado a snake_case para PostgreSQL ─────────────────────────
    df_limpio['grupo_diagnostico']          = df_limpio['grupo diagnóstico']
    df_limpio['contaminante']               = df_limpio['nombre contaminante']
    df_limpio['tipo_rezago']                = df_limpio['tipo de rezago']
    df_limpio['numero_modelo']              = df_limpio['número de modelo'].astype(int)
    df_limpio['beta']                       = df_limpio['beta del contaminante']
    df_limpio['exponencial_beta']           = df_limpio['exponencial del beta']
    df_limpio['limite_inferior']            = df_limpio['limite inferior del exponencial del beta']
    df_limpio['limite_superior']            = df_limpio['limite superior del exponencial del beta']
    df_limpio['porcentaje_incremento_riesgo'] = df_limpio['porcentaje del incremento del riesgo']

    return df_limpio
