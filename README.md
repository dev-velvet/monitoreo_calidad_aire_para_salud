# Sistema de Monitoreo de Calidad del Aire y Salud Pública (Valle de Aburrá)

Este es un proyecto diseñado para la materia **Integración y Adquisición de Datos** (2° semestre de Ciencia de Datos - ITM). Desarrolla un pipeline **ETL (Extract, Transform, Load)** completo que integra datos históricos de salud pública (mortalidad, morbilidad y análisis de riesgo por contaminantes) con datos de calidad del aire en tiempo real obtenidos de la API de **SIATA**.

Todo el sistema está diseñado para cargarse en una base de datos relacional **PostgreSQL** local.

---

## 🏗️ Arquitectura del Pipeline

El pipeline está dividido según los principios de la ingeniería de datos:

1. **Extracción (Extract)**: 
   - Lee 4 archivos CSV con datos históricos (2008-2017).
   - Consume en vivo el feed KML de la API de **SIATA** para extraer mediciones en tiempo real de PM2.5.
2. **Transformación (Transform)**:
   - Limpieza y tipificación con **Pandas** (corrección de decimales con coma, eliminación de nulos negativos, renombrado a snake_case).
   - Estandarización y normalización de textos (municipios unificados a su nombre real, edades mapeadas a categorías comunes).
3. **Carga (Load)**:
   - Diseño relacional normalizado con tablas de dimensión (`municipios`, `contaminantes`, `grupos_diagnosticos`) y tablas de hechos (`analisis_riesgo`, `enfermedades`, `tasa_mortalidad`, `defunciones`, `mediciones_siata`).
   - Inserción masiva e inteligente por lotes.
   - **Estrategia UPSERT (ON CONFLICT)** en mediciones en tiempo real para evitar registros duplicados.
4. **Automatización (Scheduler)**:
   - Un script programador (Daemon) que consulta y actualiza la API de SIATA de forma autónoma.

---

## 📂 Estructura del Proyecto

```
monitoreo_calidad_aire_para_salud/
├── fuente_datos/                         # Datos crudos del proyecto (CSVs)
│   ├── AnalisisRiesgo_20082017.csv
│   ├── EnfermedadesCalculadas_2008-2017.csv
│   ├── TasaMortalidad_2008-2017.csv
│   └── DefunsionesCalculadas_2008-2017.csv
│
├── etl/                                  # Código fuente del Pipeline ETL
│   ├── config.py                         # Configuración central (credenciales, rutas y diccionarios)
│   ├── db_postgres.py                    # DDL de PostgreSQL e inserción por lotes
│   ├── limpieza_historicos_A.py          # Script Pandas a cargo del Compañero A
│   ├── limpieza_historicos_B.py          # Script Pandas a cargo del Compañero B
│   ├── extract_siata.py                  # Cliente extractor de la API en tiempo real
│   ├── etl_pipeline.py                   # Orquestador del pipeline completo
│   ├── scheduler.py                      # Programador recurrente para capturar datos vivos
│   └── requirements.txt                  # Dependencias de Python
│
├── consultas/                            # Consultas SQL de comprobación e integración
│   └── consultas_validacion.sql
│
└── README.md                             # Documentación del proyecto (Este archivo)
```

---

## 🛠️ Instalación y Configuración

### 1. Requisitos Previos
* **Python 3.8 o superior** instalado.
* **PostgreSQL** instalado y ejecutándose localmente.

### 2. Instalación de Dependencias
Abre una terminal en la raíz del proyecto e instala las librerías necesarias ejecutando:
```bash
pip install -r etl/requirements.txt
```

### 3. Configuración de PostgreSQL
Asegúrate de que tu PostgreSQL local esté activo. Por defecto, el script de configuración en `etl/config.py` intentará conectarse usando:
* **Host**: `localhost`
* **Port**: `5432`
* **User**: `postgres`
* **Password**: `postgres`

Si tus credenciales locales son diferentes (por ejemplo, otra contraseña), cámbialas directamente en [etl/config.py](file:///c:/Users/ASUS/Documents/mariana/itm_mariana/Integracion%20y%20adquisici%C3%B3n%20de%20datos/proyecto/monitoreo_calidad_aire_para_salud/etl/config.py) o configúralas en tus variables de entorno.

---

## 🚀 Ejecución del Sistema

### Paso 1: Ejecutar el Pipeline ETL Completo
Este paso creará automáticamente la base de datos `calidad_aire_salud` (si no existe), estructurará todas las tablas relacionales con sus llaves primarias/foráneas, y procesará y cargará todos los CSVs históricos junto con las lecturas actuales de SIATA.

```bash
python etl/etl_pipeline.py
```

### Paso 2: Ejecutar el Scheduler (Automatización de SIATA)
Para mantener los datos de calidad del aire actualizados automáticamente en segundo plano:

* **Modo Producción** (ejecuta e inserta datos nuevos cada 1 hora):
  ```bash
  python etl/scheduler.py
  ```
* **Modo Demostración en Clase** (ejecuta e inserta datos cada 10 segundos, ideal para que el profesor vea la base de datos poblarse en tiempo real):
  ```bash
  python etl/scheduler.py --demo
  ```

---

## 📊 Validación de Datos
Una vez ejecutado el pipeline, puedes abrir tu cliente de base de datos favorito (pgAdmin, DBeaver, VS Code, etc.), conectarte a la base de datos `calidad_aire_salud` y correr las consultas de validación en:
👉 [consultas/consultas_validacion.sql](file:///c:/Users/ASUS/Documents/mariana/itm_mariana/Integracion%20y%20adquisici%C3%B3n%20de%20datos/proyecto/monitoreo_calidad_aire_para_salud/consultas/consultas_validacion.sql)

Estas consultas validan:
* El conteo correcto de registros cargados por tabla.
* Que no existan inconsistencias de claves foráneas.
* Cruces relacionales de riesgo por contaminantes vs morbilidad por municipios.

---

## 👥 Roles del Equipo de Trabajo
* **Tú**: Integración avanzada, API SIATA, conector de PostgreSQL, arquitectura relacional de base de datos, orquestador de pipeline y daemon scheduler.
* **Compañero A**: Carga, normalización y limpieza Pandas de `AnalisisRiesgo` y `EnfermedadesCalculadas` en [limpieza_historicos_A.py](file:///c:/Users/ASUS/Documents/mariana/itm_mariana/Integracion%20y%20adquisici%C3%B3n%20de%20datos/proyecto/monitoreo_calidad_aire_para_salud/etl/limpieza_historicos_A.py).
* **Compañero B**: Carga, normalización y limpieza Pandas de `TasaMortalidad` y `Defunciones` en [limpieza_historicos_B.py](file:///c:/Users/ASUS/Documents/mariana/itm_mariana/Integracion%20y%20adquisici%C3%B3n%20de%20datos/proyecto/monitoreo_calidad_aire_para_salud/etl/limpieza_historicos_B.py).
