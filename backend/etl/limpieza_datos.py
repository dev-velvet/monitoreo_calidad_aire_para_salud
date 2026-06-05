import os
import pandas as pd

try:
    from config import (
        CSV_ANALISIS_RIESGO,
        CSV_ENFERMEDADES,
        CSV_TASA_MORTALIDAD,
        CSV_DEFUNCIONES,
        MUNICIPIOS_MAPA,
        EDADES_MAPA
    )
except ImportError:
    from etl.config import (
        CSV_ANALISIS_RIESGO,
        CSV_ENFERMEDADES,
        CSV_TASA_MORTALIDAD,
        CSV_DEFUNCIONES,
        MUNICIPIOS_MAPA,
        EDADES_MAPA
    )

def limpiar_analisis_riesgo():
    print(f"-> Cargando y limpiando Análisis de Riesgo desde: {CSV_ANALISIS_RIESGO}")
    df = pd.read_csv(CSV_ANALISIS_RIESGO, sep=';', encoding='utf-8-sig')

    df = df[df['nombre contaminante'] == 'pm25'].reset_index(drop=True)
    print(f'Filas después del filtro PM2.5: {len(df)}')

    df_limpio = df.copy()

    cols_text = ['tipo de rezago', 'municipio', 'grupo diagnóstico', 'nombre contaminante', 'sexo', 'edad', 'rezago']
    for col in cols_text:
        df_limpio[col] = df_limpio[col].astype(str).str.strip()

    cols_num = [
        'beta del contaminante',
        'exponencial del beta',
        'limite inferior del exponencial del beta',
        'limite superior del exponencial del beta',
        'porcentaje del incremento del riesgo'
    ]
    for col in cols_num:
        df_limpio[col] = df_limpio[col].astype(str).str.replace(',', '.', regex=False).astype(float)

    duplicadas = df_limpio.duplicated().sum()
    print(f'Filas duplicadas: {duplicadas}')
    df_limpio = df_limpio.drop_duplicates()

    # Normalizar Min-Max para visualización si es necesario
    for col in cols_num:
        min_val = df_limpio[col].min()
        max_val = df_limpio[col].max()
        if max_val != min_val:
            df_limpio[col + '_normalizado'] = (df_limpio[col] - min_val) / (max_val - min_val)
        else:
            df_limpio[col + '_normalizado'] = 0.0

    # Normalización / Mapeo para PostgreSQL
    df_limpio['municipio_normalizado'] = df_limpio['municipio'].str.lower().str.strip().map(MUNICIPIOS_MAPA).fillna(df_limpio['municipio'])
    df_limpio['grupo_edad_normalizado'] = df_limpio['edad'].str.lower().str.strip().map(EDADES_MAPA).fillna(df_limpio['edad'])
    df_limpio['grupo_diagnostico'] = df_limpio['grupo diagnóstico']
    df_limpio['contaminante'] = df_limpio['nombre contaminante']
    df_limpio['tipo_rezago'] = df_limpio['tipo de rezago']
    df_limpio['numero_modelo'] = df_limpio['número de modelo'].astype(int)
    df_limpio['beta'] = df_limpio['beta del contaminante']
    df_limpio['exponencial_beta'] = df_limpio['exponencial del beta']
    df_limpio['limite_inferior'] = df_limpio['limite inferior del exponencial del beta']
    df_limpio['limite_superior'] = df_limpio['limite superior del exponencial del beta']
    df_limpio['porcentaje_incremento_riesgo'] = df_limpio['porcentaje del incremento del riesgo']
    
    return df_limpio

def limpiar_enfermedades():
    print(f"-> Cargando y limpiando Enfermedades desde: {CSV_ENFERMEDADES}")
    datos = pd.read_csv(CSV_ENFERMEDADES, sep=';', encoding='utf-8-sig')

    df_limpio = datos.copy()
    
    # Limpieza de textos y normalizaciones
    df_limpio['Municipio'] = df_limpio['Municipio'].astype(str).str.strip()
    df_limpio['Edad'] = df_limpio['Edad'].astype(str).str.strip()
    df_limpio['Sexo'] = df_limpio['Sexo'].astype(str).str.strip()
    df_limpio['Grupo'] = df_limpio['Grupo'].astype(str).str.strip()
    df_limpio['Capitulo'] = df_limpio['Capitulo'].astype(str).str.strip()
    
    # Mapeo a columnas esperadas por db_postgres.py
    df_limpio['municipio_normalizado'] = df_limpio['Municipio'].str.lower().str.strip().map(MUNICIPIOS_MAPA).fillna(df_limpio['Municipio'])
    df_limpio['grupo_edad_normalizado'] = df_limpio['Edad'].str.lower().str.strip().map(EDADES_MAPA).fillna(df_limpio['Edad'])
    df_limpio['grupo'] = df_limpio['Grupo']
    df_limpio['periodo'] = df_limpio['Periodo'].astype(int)
    df_limpio['sexo'] = df_limpio['Sexo']
    df_limpio['casos'] = df_limpio['casos'].astype(int)

    df_limpio = df_limpio.drop_duplicates()
    
    # Exportación intermedia a CSV en lugar de Excel para evitar requerir dependencias pesadas
    df_limpio.to_csv('DATOS_LIMPIOS.csv', index=False, sep=';', encoding='utf-8-sig')
    
    return df_limpio

def limpiar_tasa_mortalidad():
    print(f"-> Cargando y limpiando Tasa de Mortalidad desde: {CSV_TASA_MORTALIDAD}")
    datos = pd.read_csv(CSV_TASA_MORTALIDAD, sep=';', encoding='utf-8-sig')

    df_limpio = datos.copy()
    
    df_limpio['Municipio'] = df_limpio['Municipio'].astype(str).str.strip()
    df_limpio['Capítulo'] = df_limpio['Capítulo'].astype(str).str.strip()
    df_limpio['Sexo'] = df_limpio['Sexo'].astype(str).str.strip()
    
    # Conversión de tasa decimal
    df_limpio['TasaMortalidadAjustada'] = df_limpio['TasaMortalidadAjustada'].astype(str).str.replace(',', '.', regex=False).astype(float)
        
    df_limpio['municipio_normalizado'] = df_limpio['Municipio'].str.lower().str.strip().map(MUNICIPIOS_MAPA).fillna(df_limpio['Municipio'])
    df_limpio['anio'] = df_limpio['Año'].astype(int)
    df_limpio['capitulo'] = df_limpio['Capítulo']
    df_limpio['sexo'] = df_limpio['Sexo']
    df_limpio['tasa_ajustada'] = df_limpio['TasaMortalidadAjustada']
    
    df_limpio = df_limpio.drop_duplicates()
    
    return df_limpio

def limpiar_defunciones():
    print(f"-> Cargando y limpiando Defunciones desde: {CSV_DEFUNCIONES}")
    df = pd.read_csv(CSV_DEFUNCIONES, sep=';', encoding='utf-8-sig')

    df_limpio = df.copy()
    
    df_limpio['Municipio'] = df_limpio['Municipio'].astype(str).str.strip()
    df_limpio['Sexo'] = df_limpio['Sexo'].astype(str).str.strip()
    df_limpio['Edad'] = df_limpio['Edad'].astype(str).str.strip()
    df_limpio['Capitulo'] = df_limpio['Capitulo'].astype(str).str.strip()
    df_limpio['Grupo'] = df_limpio['Grupo'].astype(str).str.strip()
    
    df_limpio['Muertes'] = df_limpio['Muertes'].astype(str).str.replace(',', '.', regex=False).astype(float)
        
    df_limpio = df_limpio.drop_duplicates()

    # Normalizar
    min_val = df_limpio['Muertes'].min()
    max_val = df_limpio['Muertes'].max()
    if max_val != min_val:
        df_limpio['Muertes_normalizado'] = (df_limpio['Muertes'] - min_val) / (max_val - min_val)
    else:
        df_limpio['Muertes_normalizado'] = 0.0

    df_limpio['municipio_normalizado'] = df_limpio['Municipio'].str.lower().str.strip().map(MUNICIPIOS_MAPA).fillna(df_limpio['Municipio'])
    df_limpio['grupo_edad_normalizado'] = df_limpio['Edad'].str.lower().str.strip().map(EDADES_MAPA).fillna(df_limpio['Edad'])
    df_limpio['grupo'] = df_limpio['Grupo']
    df_limpio['periodo'] = df_limpio['Periodo'].astype(int)
    df_limpio['sexo'] = df_limpio['Sexo']
    df_limpio['muertes'] = df_limpio['Muertes']
    
    # Exportar archivo limpio
    df_limpio.to_csv('DefunsionesCalculadas_LIMPIO.csv', index=False, sep=';', encoding='utf-8-sig')
    
    return df_limpio
