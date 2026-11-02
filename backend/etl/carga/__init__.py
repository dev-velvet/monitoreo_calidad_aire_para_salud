"""
Módulo de Carga e Integración — FASE 3 del Pipeline ETL
=========================================================
Almacenamiento en PostgreSQL y creación de la vista consolidada
que integra las tres fuentes de datos.

Modelo relacional
-----------------
    Tablas de Dimensión (catálogos compartidos):
        - municipios           → 10 municipios del AMVA
        - contaminantes        → PM10, PM2.5, O3
        - grupos_diagnosticos  → diagnósticos CIE-10

    Tablas de Hechos (datos medidos):
        - analisis_riesgo      → coeficientes β epidemiológicos
        - enfermedades         → casos de morbilidad por período
        - tasa_mortalidad      → tasas ajustadas por municipio y sexo
        - defunciones          → conteo de defunciones por causa
        - mediciones_siata     → lecturas de PM2.5 en tiempo real

    Vista Materializada (integración):
        - vista_riesgo_integrado → JOIN de SIATA + riesgo + municipios

Estrategias de carga
--------------------
    Datos históricos:  TRUNCATE + INSERT (recarga limpia, una vez)
    Datos SIATA:       UPSERT con ON CONFLICT DO NOTHING (idempotente)
    Vista integrada:   CREATE o REFRESH MATERIALIZED VIEW

Archivos de este módulo
-----------------------
    conexion.py        →  Conexión a PostgreSQL (local o nube)
    esquema.py         →  DDL: creación de todas las tablas
    dimensiones.py     →  Población de tablas de dimensión
    hechos.py          →  Carga de datos históricos en tablas de hechos
    siata.py           →  Carga UPSERT de mediciones SIATA
    vista_integrada.py →  Creación/refresco de la vista materializada
"""

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
from etl.carga.vista_integrada import crear_vista_datos_integrados
