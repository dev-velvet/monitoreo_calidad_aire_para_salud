"""
================================================================================
SCRIPT DE LIMPIEZA Y NORMALIZACIÓN - COMPAÑERO A
Responsable: Compañero A
Materia: Integración y Adquisición de Datos
--------------------------------------------------------------------------------
Este script limpia y normaliza los siguientes archivos:
1. AnalisisRiesgo_20082017.csv
2. EnfermedadesCalculadas_2008-2017.csv

Instrucciones para Compañero A:
- Revisa las funciones 'limpiar_analisis_riesgo' y 'limpiar_enfermedades'.
- Lee los comentarios con 'EXPLICACIÓN PASO A PASO' para entender cómo Pandas
  soluciona los problemas del mundo real (separadores, decimales con comas, etc.).
================================================================================
"""

import pandas as pd
import os
from config import CSV_ANALISIS_RIESGO, CSV_ENFERMEDADES, MUNICIPIOS_MAPA, EDADES_MAPA

def limpiar_analisis_riesgo(ruta_csv=CSV_ANALISIS_RIESGO):
    """
    Carga y limpia el archivo AnalisisRiesgo_20082017.csv.
    """
    print(f"-> Compañero A: Iniciando limpieza de Analisis Riesgo desde {ruta_csv}")
    
    if not os.path.exists(ruta_csv):
        raise FileNotFoundError(f"No se encontró el archivo CSV en la ruta: {ruta_csv}")
        
    # PASO 1: Leer el CSV.
    # Nota: El archivo original utiliza punto y coma ';' como separador de columnas.
    df = pd.read_csv(ruta_csv, sep=';', encoding='utf-8')
    
    # PASO 2: Renombrar las columnas para estandarizarlas a minúsculas y snake_case (sin espacios ni acentos)
    columnas_nuevas = {
        'tipo de rezago': 'tipo_rezago',
        'número de modelo': 'numero_modelo',
        'municipio': 'municipio',
        'grupo diagnóstico': 'grupo_diagnostico',
        'nombre contaminante': 'contaminante',
        'sexo': 'sexo',
        'edad': 'grupo_edad',
        'casos': 'casos',
        'rezago': 'rezago',
        'beta del contaminante': 'beta',
        'exponencial del beta': 'exponencial_beta',
        'limite inferior del exponencial del beta': 'limite_inferior',
        'limite superior del exponencial del beta': 'limite_superior',
        'porcentaje del incremento del riesgo': 'porcentaje_incremento_riesgo'
    }
    df = df.rename(columns=columnas_nuevas)
    
    # PASO 3: Normalización de nombres de municipios
    # Pasamos a minúsculas, quitamos espacios y usamos el diccionario MUNICIPIOS_MAPA de config.py
    df['municipio_normalizado'] = df['municipio'].str.strip().str.lower().map(MUNICIPIOS_MAPA)
    # Si algún municipio no se mapeó, mantenemos el original capitalizado
    df['municipio_normalizado'] = df['municipio_normalizado'].fillna(df['municipio'].str.strip())
    
    # PASO 4: Normalización de grupos de edad
    df['grupo_edad_normalizado'] = df['grupo_edad'].str.strip().str.lower().map(EDADES_MAPA)
    df['grupo_edad_normalizado'] = df['grupo_edad_normalizado'].fillna(df['grupo_edad'].str.strip())
    
    # PASO 5: Corregir decimales que usan coma ',' en lugar de punto '.'
    # Columnas numéricas que tienen comas: beta, exponencial_beta, limite_inferior, limite_superior, porcentaje_incremento_riesgo
    columnas_decimales = ['beta', 'exponencial_beta', 'limite_inferior', 'limite_superior', 'porcentaje_incremento_riesgo']
    for col in columnas_decimales:
        if col in df.columns:
            # Reemplazar comas por puntos y convertir a tipo numérico float
            df[col] = df[col].astype(str).str.replace(',', '.')
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    # PASO 6: Limpieza y normalización del campo 'sexo'
    df['sexo'] = df['sexo'].str.strip().str.capitalize()
    
    # PASO 7: Normalización de rezago (por ejemplo "0:03" a minutos o mantener la categoría)
    df['rezago'] = df['rezago'].str.strip()
    
    print(f"[OK] Companero A: Finalizada limpieza de Analisis Riesgo. Registros: {len(df)}")
    return df


def limpiar_enfermedades(ruta_csv=CSV_ENFERMEDADES):
    """
    Carga y limpia el archivo EnfermedadesCalculadas_2008-2017.csv.
    """
    print(f"-> Compañero A: Iniciando limpieza de Enfermedades Calculadas desde {ruta_csv}")
    
    if not os.path.exists(ruta_csv):
        raise FileNotFoundError(f"No se encontró el archivo CSV en la ruta: {ruta_csv}")
        
    # PASO 1: Leer el CSV
    df = pd.read_csv(ruta_csv, sep=';', encoding='utf-8')
    
    # PASO 2: Estandarizar nombres de columnas a minúsculas
    df.columns = df.columns.str.strip().str.lower()
    
    # PASO 3: Normalización de municipios
    df['municipio_normalizado'] = df['municipio'].str.strip().str.lower().map(MUNICIPIOS_MAPA)
    df['municipio_normalizado'] = df['municipio_normalizado'].fillna(df['municipio'].str.strip())
    
    # PASO 4: Normalización de grupos de edad
    df['grupo_edad_normalizado'] = df['edad'].str.strip().str.lower().map(EDADES_MAPA)
    df['grupo_edad_normalizado'] = df['grupo_edad_normalizado'].fillna(df['edad'].str.strip())
    
    # PASO 5: Estandarizar columna sexo
    df['sexo'] = df['sexo'].str.strip().str.capitalize()
    
    # PASO 6: Asegurar que casos y periodo sean enteros
    df['casos'] = pd.to_numeric(df['casos'], errors='coerce').fillna(0).astype(int)
    df['periodo'] = pd.to_numeric(df['periodo'], errors='coerce').fillna(0).astype(int)
    
    # PASO 7: Estandarizar textos de grupos y capítulos de enfermedades
    df['grupo'] = df['grupo'].str.strip()
    df['capitulo'] = df['capitulo'].str.strip()
    
    print(f"[OK] Companero A: Finalizada limpieza de Enfermedades. Registros: {len(df)}")
    return df

if __name__ == "__main__":
    # Prueba local para validar que los scripts funcionan correctamente de forma aislada
    try:
        df_riesgo = limpiar_analisis_riesgo()
        print(df_riesgo.head(3))
        
        df_enfermedades = limpiar_enfermedades()
        print(df_enfermedades.head(3))
        print("\nTodo funciona perfecto para el Companero A!")
    except Exception as e:
        print(f"Ocurrio un error en la prueba: {e}")
