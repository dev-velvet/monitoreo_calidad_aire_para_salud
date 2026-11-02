"""
Limpieza de Datos — TasaMortalidad_2008-2017.csv
==================================================
Carga y transforma el dataset de tasas de mortalidad ajustadas
del Valle de Aburrá.

Contenido del dataset
---------------------
    - 713 registros de tasas de mortalidad
    - Desagregado por: municipio, año, capítulo diagnóstico, sexo
    - Tasa ajustada como valor numérico (usa coma como separador decimal)

Transformaciones aplicadas
--------------------------
    1. Limpieza de textos: strip() en columnas categóricas
    2. Corrección de decimales: comas → puntos en la tasa de mortalidad
    3. Normalización de nombres de municipio
    4. Eliminación de registros duplicados
"""

import pandas as pd

from etl.configuracion.settings import CSV_TASA_MORTALIDAD
from etl.configuracion.diccionarios import MUNICIPIOS_MAPA


def limpiar_tasa_mortalidad():
    """
    Carga y limpia el archivo TasaMortalidad_2008-2017.csv.

    Returns:
        pd.DataFrame limpio con columnas normalizadas listas para PostgreSQL.
    """
    print(f"-> Cargando y limpiando Tasa de Mortalidad desde: {CSV_TASA_MORTALIDAD}")
    datos = pd.read_csv(CSV_TASA_MORTALIDAD, sep=';', encoding='utf-8-sig')

    df_limpio = datos.copy()

    # ── 1. Limpieza de textos ──────────────────────────────────────────────
    df_limpio['Municipio'] = df_limpio['Municipio'].astype(str).str.strip()
    df_limpio['Capítulo']  = df_limpio['Capítulo'].astype(str).str.strip()
    df_limpio['Sexo']      = df_limpio['Sexo'].astype(str).str.strip()

    # ── 2. Corrección de decimales: comas → puntos ─────────────────────────
    df_limpio['TasaMortalidadAjustada'] = (
        df_limpio['TasaMortalidadAjustada'].astype(str)
        .str.replace(',', '.', regex=False)
        .astype(float)
    )

    # ── 3. Normalización de municipios ─────────────────────────────────────
    df_limpio['municipio_normalizado'] = (
        df_limpio['Municipio'].str.lower().str.strip()
        .map(MUNICIPIOS_MAPA)
        .fillna(df_limpio['Municipio'])
    )

    # ── 4. Mapeo a columnas para PostgreSQL ────────────────────────────────
    df_limpio['anio']          = df_limpio['Año'].astype(int)
    df_limpio['capitulo']      = df_limpio['Capítulo']
    df_limpio['sexo']          = df_limpio['Sexo']
    df_limpio['tasa_ajustada'] = df_limpio['TasaMortalidadAjustada']

    # ── 5. Eliminación de duplicados ───────────────────────────────────────
    antes = len(df_limpio)
    df_limpio = df_limpio.drop_duplicates()
    print(f'   Filas duplicadas eliminadas: {antes - len(df_limpio)}')

    return df_limpio
