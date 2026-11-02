"""
Módulo de Transformación — FASE 2 del Pipeline ETL
====================================================
Exploración, limpieza, normalización y transformación de los datos
extraídos en la Fase 1.

Transformaciones aplicadas (documentadas en perfilamiento_fuentes.md)
----------------------------------------------------------------------
1. Normalización de nombres de municipio   → diccionarios.MUNICIPIOS_MAPA
2. Normalización de grupos de edad         → diccionarios.EDADES_MAPA
3. Corrección de separadores decimales     → comas (,) → puntos (.)
4. Filtro de valores de mantenimiento SIATA → -999 → NULL
5. Clasificación de categoría ICA          → Buena / Moderada / Dañina / ... (Res. 2254 de 2017)
6. Renombrado de columnas                 → snake_case para PostgreSQL
7. Extracción de coordenadas geográficas   → latitud, longitud desde KML

Calidad de datos (respuesta a evaluadores)
-------------------------------------------
- Eliminación de duplicados con df.drop_duplicates()
- Validación de claves foráneas (registros huérfanos = 0)
- Conversión de tipos de dato para consistencia numérica

Archivos de este módulo
-----------------------
    limpieza_riesgo.py        →  Limpieza de AnalisisRiesgo_20082017.csv
    limpieza_enfermedades.py  →  Limpieza de EnfermedadesCalculadas_2008-2017.csv
    limpieza_mortalidad.py    →  Limpieza de TasaMortalidad_2008-2017.csv
    limpieza_defunciones.py   →  Limpieza de DefunsionesCalculadas_2008-2017.csv
    calidad_datos.py          →  Funciones de validación y detección de atípicos
"""

from etl.transformacion.limpieza_riesgo import limpiar_analisis_riesgo
from etl.transformacion.limpieza_enfermedades import limpiar_enfermedades
from etl.transformacion.limpieza_mortalidad import limpiar_tasa_mortalidad
from etl.transformacion.limpieza_defunciones import limpiar_defunciones
from etl.transformacion.calidad_datos import validar_calidad_datos
