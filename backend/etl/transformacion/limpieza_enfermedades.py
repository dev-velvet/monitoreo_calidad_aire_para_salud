"""
Limpieza de Datos — EnfermedadesCalculadas_2008-2017.csv
=========================================================
Carga y transforma el dataset de morbilidad por enfermedades
respiratorias del Valle de Aburrá.

Contenido del dataset
---------------------
    - Casos de enfermedades por período (2008-2017)
    - Desagregado por: municipio, sexo, grupo de edad, diagnóstico CIE-10

Transformaciones aplicadas
--------------------------
    1. Limpieza de textos: strip() en columnas categóricas
    2. Normalización de nombres de municipio y grupos de edad
    3. Eliminación de registros duplicados
    4. Exportación intermedia a CSV limpio para auditoría
"""

import pandas as pd

from etl.configuracion.settings import CSV_ENFERMEDADES
from etl.configuracion.diccionarios import MUNICIPIOS_MAPA, EDADES_MAPA


def limpiar_enfermedades():
    """
    Carga y limpia el archivo EnfermedadesCalculadas_2008-2017.csv.

    Returns:
        pd.DataFrame limpio con columnas normalizadas listas para PostgreSQL.
    """
    print(f"-> Cargando y limpiando Enfermedades desde: {CSV_ENFERMEDADES}")
    datos = pd.read_csv(CSV_ENFERMEDADES, sep=';', encoding='utf-8-sig')

    df_limpio = datos.copy()

    # ── 1. Limpieza de textos ──────────────────────────────────────────────
    for col in ['Municipio', 'Edad', 'Sexo', 'Grupo', 'Capitulo']:
        df_limpio[col] = df_limpio[col].astype(str).str.strip()

    # ── 2. Normalización de municipios y grupos de edad ────────────────────
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

    # ── 3. Mapeo a columnas esperadas por la carga en PostgreSQL ───────────
    df_limpio['grupo']   = df_limpio['Grupo']
    df_limpio['periodo'] = df_limpio['Periodo'].astype(int)
    df_limpio['sexo']    = df_limpio['Sexo']
    df_limpio['casos']   = df_limpio['casos'].astype(int)

    # ── 4. Eliminación de duplicados ───────────────────────────────────────
    antes = len(df_limpio)
    df_limpio = df_limpio.drop_duplicates()
    print(f'   Filas duplicadas eliminadas: {antes - len(df_limpio)}')

    return df_limpio
