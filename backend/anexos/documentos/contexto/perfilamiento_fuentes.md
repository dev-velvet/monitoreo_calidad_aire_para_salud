# Perfilamiento de las Fuentes de Datos

El perfilamiento de las tres fuentes de datos se realizó con **Python** utilizando las librerías **Pandas** para los CSVs históricos y **Requests + ElementTree** para la API de SIATA. No se utilizaron Open Refine ni Power Query, ya que Python permitió integrar el perfilamiento directamente dentro del pipeline ETL, automatizando todo el proceso desde la lectura hasta la carga.

Se realizaron las siguientes **transformaciones** sobre las fuentes:

1. **Normalización de nombres de municipio**: Los CSVs contenían variantes como `medellin`, `Medellín`, `itagui`, `Itagüí`. Se creó un diccionario `MUNICIPIOS_MAPA` que mapea cada variante al nombre oficial estándar, aplicado con `pandas.Series.apply()` sobre la columna original.

2. **Normalización de grupos de edad**: Las edades aparecían como `menores de 5 años`, `menor de 5 años`, `5 a 14`, `65+`, etc. Se unificaron a categorías comunes mediante el diccionario `EDADES_MAPA`.

3. **Corrección de separadores decimales**: Los CSVs usaban coma como separador decimal (ej. `0,2318`). Se aplicó `str.replace(',', '.')` y conversión a `float` en todas las columnas numéricas (betas, tasas, límites).

4. **Filtro de valores de mantenimiento de SIATA**: La API devuelve `-999` cuando una estación está en mantenimiento. Se convirtieron estos valores a `None` (NULL en la base de datos) para evitar sesgos en los cálculos de promedios.

5. **Clasificación de categoría ICA**: A partir del valor de PM2.5 se asignó una categoría según los puntos de corte de la Resolución 2254 de 2017 (Buena, Aceptable, Dañina a la salud de grupos sensibles, Dañina para la salud, Muy dañina para la salud, Peligrosa).

6. **Renombrado de columnas**: Los CSVs tenían nombres en español con espacios (`beta del contaminante`, `porcentaje del incremento del riesgo`). Se renombraron a snake_case (`beta`, `porcentaje_incremento_riesgo`) para consistencia con el esquema de la base de datos.

7. **Extracción de coordenadas geográficas**: Desde el feed KML de SIATA se parsearon las coordenadas (`<coordinates>`) de cada estación, separando longitud y latitud en columnas independientes.

Como **columnas adicionales** creadas, en la fuente de `AnalisisRiesgo` se generaron:
- **`municipio_normalizado`**: derivada de la columna original `municipio` después de aplicar el diccionario de normalización.
- **`grupo_edad_normalizado`**: derivada de la columna original `edad` después de unificar rangos etarios.

En la fuente SIATA se crearon adicionalmente:
- **`categoria_ica`**: clasificación textual del nivel de PM2.5 según estándares de calidad del aire.
- **`fecha_carga`**: timestamp del momento en que se extrajo el dato, generado automáticamente con `datetime.now()`.
