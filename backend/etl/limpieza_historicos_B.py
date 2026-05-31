"""
================================================================================
SCRIPT DE LIMPIEZA Y NORMALIZACIÓN - COMPAÑERO B
Responsable: Compañero B
Materia: Integración y Adquisición de Datos
--------------------------------------------------------------------------------
Este script limpia y normaliza los siguientes archivos:
1. TasaMortalidad_2008-2017.csv
2. DefunsionesCalculadas_2008-2017.csv

Instrucciones para Compañero B:
- Revisa las funciones 'limpiar_tasa_mortalidad' y 'limpiar_defunciones'.
- Lee los comentarios con 'EXPLICACIÓN PASO A PASO' para entender cómo Pandas
  soluciona los problemas del mundo real (separadores, decimales con comas, etc.).
================================================================================
"""

import pandas as pd
import os
from config import CSV_TASA_MORTALIDAD, CSV_DEFUNCIONES, MUNICIPIOS_MAPA, EDADES_MAPA

def limpiar_tasa_mortalidad(ruta_csv=CSV_TASA_MORTALIDAD):
    """
    Carga y limpia el archivo TasaMortalidad_2008-2017.csv.
    """
    print(f"-> Compañero B: Iniciando limpieza de Tasa de Mortalidad desde {ruta_csv}")
    
    if not os.path.exists(ruta_csv):
        raise FileNotFoundError(f"No se encontró el archivo CSV en la ruta: {ruta_csv}")
        
    # PASO 1: Leer el CSV.
    # El archivo original utiliza punto y coma ';' como separador
    df = pd.read_csv(ruta_csv, sep=';', encoding='utf-8')
    
    # PASO 2: Estandarizar nombres de columnas a minúsculas y snake_case
    columnas_nuevas = {
        'Año': 'anio',
        'Municipio': 'municipio',
        'Capítulo': 'capitulo',
        'Sexo': 'sexo',
        'TasaMortalidadAjustada': 'tasa_ajustada'
    }
    df = df.rename(columns=columnas_nuevas)
    
    # PASO 3: Normalización de municipios
    df['municipio_normalizado'] = df['municipio'].str.strip().str.lower().map(MUNICIPIOS_MAPA)
    df['municipio_normalizado'] = df['municipio_normalizado'].fillna(df['municipio'].str.strip())
    
    # PASO 4: Estandarizar sexo (por ejemplo, "Hombres" -> "Hombre", "Mujeres" -> "Mujer", "Ambos sexos" -> "Ambos sexos")
    df['sexo'] = df['sexo'].str.strip()
    sexo_mapeo = {
        'Hombres': 'Hombre',
        'Mujeres': 'Mujer',
        'Ambos sexos': 'Ambos sexos'
    }
    df['sexo'] = df['sexo'].map(sexo_mapeo).fillna(df['sexo'])
    
    # PASO 5: Corregir decimal en tasa_ajustada (cambiar comas por puntos y castear a float)
    if 'tasa_ajustada' in df.columns:
        df['tasa_ajustada'] = df['tasa_ajustada'].astype(str).str.replace(',', '.')
        df['tasa_ajustada'] = pd.to_numeric(df['tasa_ajustada'], errors='coerce')
        
    # PASO 6: Asegurar que el año sea un entero
    df['anio'] = pd.to_numeric(df['anio'], errors='coerce').fillna(0).astype(int)
    
    # PASO 7: Limpiar espacios extras en capítulos
    df['capitulo'] = df['capitulo'].str.strip()
    
    print(f"[OK] Companero B: Finalizada limpieza de Tasa de Mortalidad. Registros: {len(df)}")
    return df


def limpiar_defunciones(ruta_csv=CSV_DEFUNCIONES):
    """
    Carga y limpia el archivo DefunsionesCalculadas_2008-2017.csv.
    """
    print(f"-> Compañero B: Iniciando limpieza de Defunciones Calculadas desde {ruta_csv}")
    
    if not os.path.exists(ruta_csv):
        raise FileNotFoundError(f"No se encontró el archivo CSV en la ruta: {ruta_csv}")
        
    # PASO 1: Leer el CSV con separador ';'
    df = pd.read_csv(ruta_csv, sep=';', encoding='utf-8')
    
    # PASO 2: Estandarizar nombres de columnas a minúsculas
    df.columns = df.columns.str.strip().str.lower()
    
    # PASO 3: Normalización de municipios
    df['municipio_normalizado'] = df['municipio'].str.strip().str.lower().map(MUNICIPIOS_MAPA)
    df['municipio_normalizado'] = df['municipio_normalizado'].fillna(df['municipio'].str.strip())
    
    # PASO 4: Normalización de grupos de edad
    df['grupo_edad_normalizado'] = df['edad'].str.strip().str.lower().map(EDADES_MAPA)
    df['grupo_edad_normalizado'] = df['grupo_edad_normalizado'].fillna(df['edad'].str.strip())
    
    # PASO 5: Estandarizar sexo
    df['sexo'] = df['sexo'].str.strip().str.capitalize()
    
    # PASO 6: Corregir muertes (decimal con comas a float)
    if 'muertes' in df.columns:
        df['muertes'] = df['muertes'].astype(str).str.replace(',', '.')
        df['muertes'] = pd.to_numeric(df['muertes'], errors='coerce')
        
    # PASO 7: Asegurar que el periodo sea entero
    df['periodo'] = pd.to_numeric(df['periodo'], errors='coerce').fillna(0).astype(int)
    
    # PASO 8: Limpiar espacios extras en texto
    df['capitulo'] = df['capitulo'].str.strip()
    df['grupo'] = df['grupo'].str.strip()
    
    print(f"[OK] Companero B: Finalizada limpieza de Defunciones. Registros: {len(df)}")
    return df

if __name__ == "__main__":
    # Prueba local para validar que los scripts funcionan correctamente de forma aislada
    try:
        df_mortalidad = limpiar_tasa_mortalidad()
        print(df_mortalidad.head(3))
        
        df_defunciones = limpiar_defunciones()
        print(df_defunciones.head(3))
        print("\nTodo funciona perfecto para el Companero B!")
    except Exception as e:
        print(f"Ocurrio un error en la prueba: {e}")
