"""
Limpieza de Datos — DefunsionesCalculadas_2008-2017.csv
========================================================
Carga y transforma el dataset de defunciones por enfermedades
respiratorias y cardiovasculares del Valle de Aburrá.

Contenido del dataset
---------------------
    - Conteo de defunciones por período (2008-2017)
    - Desagregado por: municipio, sexo, grupo de edad, diagnóstico CIE-10

Transformaciones aplicadas
--------------------------
    1. Limpieza de textos: strip() en columnas categóricas
    2. Corrección de decimales: comas → puntos en la columna Muertes
    3. Eliminación de registros duplicados
    4. Normalización Min-Max de la columna Muertes
    5. Normalización de nombres de municipio y grupos de edad
"""

import pandas as pd

from etl.configuracion.settings import CSV_DEFUNCIONES
from etl.configuracion.diccionarios import MUNICIPIOS_MAPA, EDADES_MAPA


def limpiar_defunciones():
    """
    Carga y limpia el archivo DefunsionesCalculadas_2008-2017.csv.

    Returns:
        pd.DataFrame limpio con columnas normalizadas listas para PostgreSQL.
    """
    print(f"-> Cargando y limpiando Defunciones desde: {CSV_DEFUNCIONES}")
    df = pd.read_csv(CSV_DEFUNCIONES, sep=';', encoding='utf-8-sig')

    df_limpio = df.copy()

    # ── 1. Limpieza de textos ──────────────────────────────────────────────
    for col in ['Municipio', 'Sexo', 'Edad', 'Capitulo', 'Grupo']:
        df_limpio[col] = df_limpio[col].astype(str).str.strip()

    # ── 2. Corrección de decimales: comas → puntos ─────────────────────────
    df_limpio['Muertes'] = (
        df_limpio['Muertes'].astype(str)
        .str.replace(',', '.', regex=False)
        .astype(float)
    )

    # ── 3. Eliminación de duplicados ───────────────────────────────────────
    antes = len(df_limpio)
    df_limpio = df_limpio.drop_duplicates()
    print(f'   Filas duplicadas eliminadas: {antes - len(df_limpio)}')

    # ── 4. Normalización Min-Max ───────────────────────────────────────────
    min_val = df_limpio['Muertes'].min()
    max_val = df_limpio['Muertes'].max()
    if max_val != min_val:
        df_limpio['Muertes_normalizado'] = (df_limpio['Muertes'] - min_val) / (max_val - min_val)
    else:
        df_limpio['Muertes_normalizado'] = 0.0

    # ── 5. Normalización de municipios y grupos de edad ────────────────────
    df_limpio['municipio_normalizado'] = (
        df_limpio['Municipio'].str.lower().str.strip()
        .map(MUNICIPIOS_MAPA)
        .fillna(df_limpio['Municipio'])
    )
    df_limpio['grupo_edad_normalizado'] = (
        df_limpio['Edad'].str.lower().str.strip()
        .map(EDADES_MAPA)
        .fillna(df_limpio['Edad'])
    )

    # ── 6. Mapeo a columnas para PostgreSQL ────────────────────────────────
    df_limpio['grupo']   = df_limpio['Grupo']
    df_limpio['periodo'] = df_limpio['Periodo'].astype(int)
    df_limpio['sexo']    = df_limpio['Sexo']
    df_limpio['muertes'] = df_limpio['Muertes']

    return df_limpio
