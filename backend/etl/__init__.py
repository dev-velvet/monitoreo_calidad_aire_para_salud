"""
Paquete ETL — Pipeline de Adquisición e Integración de Datos
=============================================================
Calidad del Aire y Salud Pública del Valle de Aburrá

Este paquete implementa el proceso ETL (Extracción, Transformación y Carga)
descrito en la sección de Metodología del paper. Está organizado en módulos
que corresponden directamente a las fases del pipeline:

Estructura del paquete
----------------------
    etl/
    ├── configuracion/      →  Parámetros centralizados del sistema
    │   ├── settings.py     →  Conexión BD, URL del API SIATA, rutas de archivos
    │   └── diccionarios.py →  Diccionarios de normalización (municipios, edades)
    │
    ├── extraccion/         →  FASE 1: Identificación y extracción de fuentes
    │   └── siata_api.py    →  Extracción de la API KML del SIATA (fuente primaria)
    │
    ├── transformacion/     →  FASE 2: Exploración, limpieza y transformación
    │   ├── limpieza_riesgo.py        →  Limpieza de AnalisisRiesgo_20082017.csv
    │   ├── limpieza_enfermedades.py  →  Limpieza de EnfermedadesCalculadas_2008-2017.csv
    │   ├── limpieza_mortalidad.py    →  Limpieza de TasaMortalidad_2008-2017.csv
    │   ├── limpieza_defunciones.py   →  Limpieza de DefunsionesCalculadas_2008-2017.csv
    │   └── calidad_datos.py          →  Validación de calidad y detección de atípicos
    │
    ├── carga/              →  FASE 3: Integración y carga en PostgreSQL
    │   ├── conexion.py     →  Conexión a PostgreSQL (local o nube)
    │   ├── esquema.py      →  DDL: tablas de dimensión y de hechos
    │   ├── dimensiones.py  →  Población de tablas de dimensión (municipios, CIE-10)
    │   ├── hechos.py       →  Carga de datos históricos en tablas de hechos
    │   ├── siata.py        →  Carga UPSERT de mediciones SIATA (tiempo real)
    │   └── vista_integrada.py → Vista materializada: integración de 3 fuentes
    │
    ├── pipeline.py         →  Orquestador principal del pipeline ETL completo
    └── scheduler.py        →  Daemon de extracción periódica automatizada

Ejecución
---------
    # Pipeline completo (desde backend/):
    python -m etl.pipeline

    # Scheduler automático:
    python -m etl.scheduler          # Producción: cada 1 hora
    python -m etl.scheduler --demo   # Demostración: cada 10 segundos
"""
