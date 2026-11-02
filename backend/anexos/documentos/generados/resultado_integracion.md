# Resultado de la Integración de Datos

## Pipeline de Datos

El pipeline de datos del proyecto sigue un flujo ETL estructurado en cinco etapas:

**1. Adquisición conceptual**: Se identificaron tres fuentes de datos: la API de SIATA (mediciones de PM2.5 en tiempo real, consultada cada 2 minutos), cuatro archivos CSV históricos de salud pública del Valle de Aburrá (AnalisisRiesgo, EnfermedadesCalculadas, TasaMortalidad y Defunciones, período 2008–2017), y el portal SISAIRE del IDEAM como fuente complementaria de referencia.

**2. Extracción**: Los CSVs se leen con `pandas.read_csv(sep=';')` y la API SIATA se consulta mediante HTTP GET sobre su feed KML, parseando el XML con `ElementTree` para extraer estación, PM2.5, coordenadas y fecha.

**3. Transformación y Corrección de Errores**: Sobre los CSVs se normalizan nombres de municipio y grupos de edad mediante diccionarios, se corrigen decimales con coma reemplazándolos por punto, y se renombran columnas a snake_case. Sobre SIATA se filtran valores `-999` (estaciones en mantenimiento) convirtiéndolos a NULL, se clasifica cada lectura en categorías ICA y se extraen coordenadas.

**4. Integración**: Los datos limpios se organizan en un modelo relacional en PostgreSQL con tablas de dimensión (municipios, contaminantes, grupos de diagnóstico) y tablas de hechos (analisis_riesgo, enfermedades, tasa_mortalidad, defunciones, mediciones_siata), conectadas mediante identificadores únicos que permiten cruzarlas con JOINs.

**5. Carga y Consumo**: Los datos históricos se cargan reemplazando registros anteriores. Los datos de SIATA se insertan cada 2 minutos evitando duplicados. Una API REST en FastAPI expone consultas SQL que cruzan las tablas, alimentando un dashboard interactivo con calculadora de riesgo en vivo.

## Resultado de la Integración

La integración produjo una base de datos relacional en PostgreSQL (Neon.tech) con 2.402 registros integrados que cruzan las tres fuentes: cada fila vincula una estación SIATA con su municipio, la medición actual de PM2.5, la categoría ICA, la enfermedad respiratoria asociada, el coeficiente beta histórico y el incremento de riesgo calculado.

En `backend/anexos/` se adjuntan (rutas desde la raíz del proyecto):
- **`backend/anexos/notebooks/integracion_datos.ipynb`**: Notebook que ejecuta la consulta de integración, muestra el DataFrame resultante y exporta el archivo final.
- **`backend/anexos/datos/integrados/datos_integrados.csv`**: Archivo con los 2.402 registros integrados de las tres fuentes.
- **`backend/anexos/datos/limpios/DATOS_LIMPIOS.csv`**: Salida limpia del histórico de análisis de riesgo.
- **`backend/anexos/datos/limpios/DefunsionesCalculadas_LIMPIO.csv`**: Salida limpia del histórico de defunciones.

## Contribución al Objetivo SMART

El objetivo planteado fue integrar mediciones de PM2.5 de la red SIATA con datos históricos de salud del Valle de Aburrá (2008–2017) en una base de datos relacional, permitiendo cruzar en tiempo real la exposición actual a contaminantes con coeficientes de riesgo epidemiológico, y exponer los resultados mediante una API para un dashboard interactivo.

El proceso diseñado contribuye directamente a este objetivo: la adquisición automática cada 2 minutos garantiza datos actualizados de contaminación; la limpieza y normalización asegura que los registros de salud sean comparables entre municipios; el modelo relacional permite que una consulta SQL cruce instantáneamente el PM2.5 de una estación SIATA con el coeficiente beta histórico del mismo municipio; y la API REST entrega estos cálculos al dashboard para su visualización. La tabla integrada resultante es la evidencia de que las tres fuentes convergen en un solo esquema capaz de responder preguntas como el incremento de riesgo de enfermedad respiratoria ante la exposición actual a PM2.5.
