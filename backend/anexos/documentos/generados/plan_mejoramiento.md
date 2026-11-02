# Plan de Mejoramiento del Paper — Simposio de Ingeniería

> **Documento base:** `documento_evaluado.md`
> **Comentarios evaluadores:** `comentarios_evaluadores.md`
> **Fecha de elaboración:** 2026-10-31

---

## 1. Resumen Ejecutivo

### Valoración general

Los evaluadores reconocen que el proyecto aborda una problemática pertinente del campo de la ingeniería y que las referencias son adecuadas. Sin embargo, las observaciones principales apuntan a cinco brechas del paper:

1. **Falta de reproducibilidad metodológica:** la metodología no detalla suficientemente cómo se integran las estaciones SIATA con la información epidemiológica a nivel geográfico y temporal, ni se explicita la función de agregación usada (suma, promedio, mediana).
2. **Debilidad en la argumentación del problema y la novedad:** el paper no presenta indicadores concretos que midan la relación PM2.5–salud ni distingue su aporte frente a integraciones similares ya publicadas.
3. **Errores de edición y formato:** erratas textuales, referencia a una Figura 2 inexistente, numeración incorrecta de fases, y la Figura 1 no cumple con el formato esperado de diagrama de flujo.
4. **Insuficiencia de apoyo gráfico y evidencia de resultados:** falta la base de datos integrada, documentación del pipeline y figuras que muestren la solución funcionando.
5. **Asincronía temporal entre datos de riesgo y datos SIATA:** los datos epidemiológicos son de 2008–2017 mientras las mediciones SIATA son en tiempo real, lo cual debilita el aporte percibido.

### Las 5 prioridades principales

| # | Prioridad | Impacto |
|---|-----------|---------|
| 1 | Reescribir la metodología para hacerla reproducible (funciones de agregación, delimitación geográfica, estructura de datos) | **Crítico** — afecta a dos evaluadores |
| 2 | Fortalecer la argumentación del problema (causas, consecuencias, indicadores) y explicitar la novedad | **Crítico** — afecta pertinencia y originalidad |
| 3 | Corregir todos los errores de edición y formato (erratas, figuras, numeración de fases, estilo IEEE) | **Alto** — son correcciones directas y rápidas |
| 4 | Añadir apoyo gráfico real del sistema: diagrama de flujo ETL, capturas del dashboard, tabla de datos integrados | **Alto** — ya existe material en el proyecto |
| 5 | Justificar explícitamente la validez de usar coeficientes β históricos con mediciones actuales | **Medio** — existe argumentación preparada en el proyecto |

---

## 2. Tabla de Trazabilidad

| # | Comentario del evaluador | Sección afectada | Acción de mejora | Evidencia/recurso existente en el proyecto | Prioridad | Esfuerzo estimado |
|---|--------------------------|------------------|-------------------|---------------------------------------------|-----------|-------------------|
| C1 | [Ev2] Falta profundizar en causas y consecuencias del problema; ausencia de indicadores que midan la relación PM2.5–enfermedades | Introducción | Ampliar la contextualización del problema con datos de morbilidad del AMVA y citar indicadores epidemiológicos (β, incremento de riesgo %) | CSVs en `backend/anexos/datos/crudos/` contienen datos de 1,652 registros de análisis de riesgo con coeficientes β; `backend/anexos/documentos/contexto/fundamentacion.md` tiene la argumentación de la relación β–PM2.5 | Alta | 2 h |
| C2 | [Ev1] La metodología no es 100% reproducible | Metodología (todas las fases) | Detallar versiones de librerías, parámetros de conexión, frecuencia de extracción, funciones de agregación, y pseudocódigo del pipeline | `backend/requirements.txt`, `backend/etl/configuracion/`, `backend/etl/pipeline.py`, `backend/etl/extraccion/siata_api.py` | Alta | 3 h |
| C3 | [Ev2] No se aclara cómo se integran las estaciones (>13) con la información epidemiológica por municipio; no se delimita la localización | Metodología — Fase 3 / Integración | Explicar el mecanismo de JOIN por nombre normalizado (`estacion ILIKE '%municipio%'`), los 10 municipios del AMVA y las ~23 estaciones; incluir el mapa de correspondencia | `backend/etl/carga/vista_integrada.py` (JOIN ILIKE), `backend/etl/configuracion/diccionarios.py` (MUNICIPIOS_MAPA) | Alta | 2 h |
| C4 | [Ev2] No se explicita la función de agregación (suma, promedio, mediana) para datos de estaciones con frecuencia cada 15 min | Metodología — Fase 3 | Especificar que se usa `DISTINCT ON (estacion) ... ORDER BY fecha_hora DESC` para tomar la medición más reciente por estación, no un agregado temporal | `backend/etl/carga/vista_integrada.py` (CTE `ultima_siata`), `backend/app/routers/siata.py` L12-17 | Alta | 1 h |
| C5 | [Ev2] Falta explicitar la estructura de datos de las variables a integrar | Metodología | Incluir tabla con el diccionario de datos de cada fuente y del modelo relacional final | `backend/anexos/documentos/contexto/perfilamiento_fuentes.md`, DDL en `backend/etl/carga/esquema.py` | Alta | 2 h |
| C6 | [Ev2] Plantear técnicas de identificación de atípicos y calidad de datos | Metodología — Transformación | Documentar: filtro de valores −999 (mantenimiento SIATA → NULL), eliminación de duplicados, validación de claves foráneas, normalización de municipios y edades | `backend/etl/extraccion/siata_api.py` (filtro −999), `backend/etl/transformacion/limpieza_riesgo.py` (duplicados), `backend/consultas/consultas_validacion.sql` L30-33 (huérfanos) | Alta | 1.5 h |
| C7 | [Ev1] Datos de riesgo y SIATA no sincronizados en el tiempo → aporte medio | Introducción + Conclusiones | Añadir párrafo justificando la validez de usar coeficientes β históricos con PM2.5 actual (son relaciones biológicas estables, enfoque estándar OMS) y reconocer como limitación explícita | `backend/anexos/documentos/contexto/fundamentacion.md` (argumentación completa), ref. [5] AirQ+ OMS | Media | 1.5 h |
| C8 | [Ev2] Falta explicitar la novedad frente a integraciones similares ya publicadas | Introducción + Originalidad | Agregar párrafo diferenciador: cálculo de riesgo personalizado (municipio × sexo × edad × diagnóstico) en tiempo real vía API, no solo un índice genérico | `backend/app/routers/salud.py` L117-269 (calculadora de riesgo cruzado con fallbacks), `backend/anexos/documentos/contexto/fundamentacion.md` L30-61 | Media | 1.5 h |
| C9 | [Ev1] Errores de edición: "2018y 2023", "HTTP GET la API", referencia a Fig. 2 inexistente, "2.2 Fase 1" debería ser "Fase 2" | Introducción, Metodología | Corregir cada errata puntualmente | Correcciones textuales directas | Alta | 0.5 h |
| C10 | [Ev1] La Figura 1 no está correctamente presentada; debe ser un diagrama de flujo o esquemático acorde | Metodología | Reemplazar por el diagrama de flujo ETL en Mermaid ya existente, renderizado como imagen de alta calidad | `backend/anexos/documentos/generados/diagrama_flujo.md` (diagrama Mermaid completo de 6 etapas) | Alta | 1 h |
| C11 | [Ev2] Se hubiera agradecido apoyo gráfico y la base de datos integrada o documentación del pipeline | Resultados | Agregar: (a) captura/tabla del `datos_integrados.csv`, (b) captura de la vista `vista_riesgo_integrado`, (c) captura del dashboard AireSalud | `backend/anexos/datos/integrados/datos_integrados.csv` (2,402 registros), `backend/anexos/documentos/generados/resultado_integracion.md`, dashboard en `https://airwise-health.onrender.com` | Alta | 2 h |
| C12 | [Ev2] El alcance podría ampliarse hacia la visualización de la información | Resultados + Conclusiones | Describir el dashboard interactivo ya implementado (mapa Leaflet, calculadora de riesgo, gráficos históricos) como resultado adicional | `guion_pitch.md` (describe las 3 secciones del dashboard), URL del frontend desplegado | Media | 1 h |
| C13 | [Formato] Garantizar tamaño carta, márgenes 2.5 cm, Times New Roman 12pt, interlineado 1.5 | Todo el documento | Aplicar formato al generar el documento final en Word/LaTeX | Especificación en `indicaciones_entrega_final.md` | Alta | 0.5 h |
| C14 | [Formato] Figuras y tablas numeradas, con leyenda, citadas en el texto | Figuras y tablas | Renumerar todas las figuras y tablas secuencialmente; agregar leyendas descriptivas; verificar que cada una se cite en el texto por su número | Verificación manual | Alta | 1 h |
| C15 | [Formato] Estilo IEEE: citas numeradas entre corchetes por orden de aparición | Referencias | Verificar que todas las citas usen [n] y no apellido-año; corregir numeración secuencial | Actualmente el paper ya usa [1]–[12] pero hay que verificar consistencia | Media | 0.5 h |
| C16 | [Formato] Al menos 8 referencias, todas citadas en el texto | Referencias | Verificar cobertura; actualmente hay ~12 referencias, confirmar que todas se citen en texto | Contar citas en `documento_evaluado.md` | Baja | 0.5 h |
| C17 | [Formato] Al menos 4 referencias de los últimos 5 años | Referencias | Verificar: refs [1](2020), [2](2024), [4](2025), [6](2024), [7](2025) cumplen. Documentar | Verificación directa de las fechas | Baja | 0.25 h |
| C18 | [Ev1] Referencia [4] y [7] son el mismo artículo (Sserunjogi et al.) duplicado | Referencias | Eliminar la referencia duplicada y renumerar | `documento_evaluado.md` L200-201 y L207 | Alta | 0.25 h |

---

## 3. Detalle por Tema

### 3.1 Pertinencia temática y contextualización del problema (C1, C7, C8)

**Qué cambiar:** Ampliar la Introducción con:
- Indicadores cuantitativos de la relación PM2.5–salud (coeficientes β y porcentajes de incremento de riesgo) ya calculados en el proyecto.
- Causas y consecuencias del problema con mayor profundidad.
- Un párrafo que justifique por qué la asincronía temporal (datos 2008–2017 vs. mediciones actuales) no invalida el aporte.
- Un párrafo que diferencie esta propuesta de integraciones previas.

**Cómo hacerlo:**

1. **Indicadores concretos:** Extraer del archivo `backend/anexos/datos/crudos/AnalisisRiesgo_20082017.csv` ejemplos de coeficientes β por municipio y grupo diagnóstico. Mencionar que el proyecto contiene 1,652 registros con coeficientes epidemiológicos desagregados por municipio, sexo, edad y diagnóstico CIE-10.

2. **Justificación de validez temporal:** Utilizar la argumentación de `backend/anexos/documentos/contexto/fundamentacion.md`:

   > **Ejemplo de reescritura (párrafo nuevo para Introducción):**
   >
   > *"Si bien los registros epidemiológicos corresponden al período 2008–2017, los coeficientes β representan relaciones biológicas exposición-respuesta entre la concentración de PM2.5 y la incidencia de enfermedades respiratorias, las cuales son estructuralmente estables en el tiempo. Este enfoque es consistente con la práctica estándar en epidemiología ambiental: la propia OMS publica funciones exposición-respuesta que se aplican durante años sin modificación [5]. Así, al multiplicar estos coeficientes por las concentraciones de PM2.5 medidas en tiempo real por la red SIATA, se obtiene una estimación de riesgo epidemiológico actualizada y territorialmente diferenciada."*

3. **Diferenciador de novedad:** Explicitar que, a diferencia de trabajos previos que generan índices de calidad del aire genéricos (como el ICA), este pipeline calcula un Índice de Riesgo Local personalizado por municipio, sexo, grupo etario y diagnóstico CIE-10, y lo expone mediante una API REST en tiempo real.

   > **Ejemplo de reescritura (párrafo nuevo para Introducción):**
   >
   > *"A diferencia de las integraciones ETL existentes en la literatura [4], [6], que se centran en la gestión y el preprocesamiento de datos ambientales, la propuesta aquí presentada va un paso más allá: fusiona las mediciones ambientales en tiempo real con coeficientes epidemiológicos históricos desagregados por municipio, sexo, grupo etario y diagnóstico según la codificación CIE-10, para calcular un incremento de riesgo epidemiológico personalizado mediante la fórmula ΔR = (e^(β · PM2.5/10) − 1) × 100, expuesto dinámicamente a través de una API REST parametrizada."*

**Archivos de referencia:**
- `backend/anexos/documentos/contexto/fundamentacion.md` — Argumentación completa sobre validez de β históricos
- `backend/anexos/datos/crudos/AnalisisRiesgo_20082017.csv` — Coeficientes β desagregados
- `backend/app/routers/salud.py` L239-240 — Implementación de la fórmula de riesgo

---

### 3.2 Rigor metodológico y reproducibilidad (C2, C3, C4, C5, C6)

Este es el bloque más crítico. Los evaluadores requieren:

#### 3.2.1 Delimitación geográfica y correspondencia estaciones–municipios (C3)

**Qué cambiar:** En la sección de Metodología, agregar un párrafo que explique:
- El estudio se delimita a los **10 municipios del Área Metropolitana del Valle de Aburrá**: Medellín, Bello, Envigado, Itagüí, Sabaneta, Caldas, Copacabana, La Estrella, Girardota y Barbosa.
- Las estaciones SIATA (~23 activas) se vinculan al municipio correspondiente mediante una coincidencia textual normalizada: `estacion ILIKE '%' || municipio.nombre_normalizado || '%'`.
- El diccionario de normalización `MUNICIPIOS_MAPA` estandariza variantes ortográficas.

**Archivos de evidencia:**
- `backend/etl/configuracion/diccionarios.py` — Diccionario `MUNICIPIOS_MAPA` con los 10 municipios
- `backend/etl/carga/vista_integrada.py` — JOIN: `us.estacion ILIKE '%' || m.nombre_normalizado || '%'`

> **Ejemplo de reescritura (sección Fase 3):**
>
> *"La integración geográfica entre las estaciones de monitoreo del SIATA y los municipios del AMVA se realizó mediante una operación JOIN textual normalizada: cada nombre de estación se compara con el nombre estandarizado del municipio (e.g., `estacion ILIKE '%Medellín%'`), utilizando un diccionario de normalización que mapea variantes ortográficas presentes en las fuentes (e.g., 'medellin' → 'Medellín', 'itagui' → 'Itagüí'). El estudio se delimita a los 10 municipios del AMVA: Medellín, Bello, Envigado, Itagüí, Sabaneta, Caldas, Copacabana, La Estrella, Girardota y Barbosa. Cuando un municipio no cuenta con estación asociada, el sistema calcula un promedio regional como respaldo."*

#### 3.2.2 Función de agregación temporal (C4)

**Qué cambiar:** Explicitar que **no se usa una función de agregación temporal** (suma, promedio, mediana) sobre las mediciones de alta frecuencia. En su lugar, se implementa una estrategia `DISTINCT ON (estacion) ORDER BY fecha_hora DESC` que selecciona la **medición más reciente** por estación.

**Archivos de evidencia:**
- `backend/etl/carga/vista_integrada.py` — CTE `ultima_siata`
- `backend/app/routers/siata.py` L12-17 — Endpoint `/api/siata/actual`

> **Ejemplo de reescritura:**
>
> *"Para la dimensión temporal, se implementó una estrategia de selección de la observación más reciente por estación (`DISTINCT ON (estacion) ORDER BY fecha_hora DESC`), priorizando la actualidad del dato sobre la suavización estadística. Esta decisión se fundamenta en que el objetivo del sistema es reflejar el estado ambiental instantáneo para cruzarlo con los coeficientes epidemiológicos, no promediar series históricas de lecturas del sensor."*

#### 3.2.3 Estructura de datos de las variables integradas (C5)

**Qué cambiar:** Incluir en la sección de Metodología una tabla resumen del modelo relacional con las dimensiones y hechos, y un breve diccionario de datos de las variables clave.

**Archivos de evidencia:**
- `backend/etl/carga/esquema.py` — DDL completo con tipos de dato
- `backend/anexos/documentos/contexto/perfilamiento_fuentes.md` — 7 transformaciones documentadas
- `metodologia_reproducible.md` §3.2 — Modelo relacional (dimensiones y hechos)

**Tabla sugerida para incluir en el paper (resumen del modelo):**

| Tipo | Tabla | Campos clave | Tipo dato | Relaciones |
|------|-------|-------------|-----------|------------|
| Dimensión | `municipios` | `id`, `nombre_normalizado` | SERIAL, VARCHAR | FK en todas las tablas de hechos |
| Dimensión | `contaminantes` | `id`, `nombre` | SERIAL, VARCHAR | FK en `analisis_riesgo` |
| Dimensión | `grupos_diagnosticos` | `id`, `nombre`, `codigo_cie10` | SERIAL, VARCHAR | FK en hechos de salud |
| Hecho | `analisis_riesgo` | `beta`, `porcentaje_incremento_riesgo`, `sexo`, `grupo_edad` | NUMERIC, VARCHAR | FK: municipio, diagnóstico, contaminante |
| Hecho | `mediciones_siata` | `estacion`, `pm25_ica`, `fecha_hora`, `latitud`, `longitud` | VARCHAR, NUMERIC, TIMESTAMP | UNIQUE(estacion, fecha_hora) |
| Vista | `vista_riesgo_integrado` | Campos cruzados de SIATA + riesgo + municipios | — | JOIN de 4 tablas |

#### 3.2.4 Técnicas de calidad de datos y detección de atípicos (C6)

**Qué cambiar:** En la subsección de Transformación, documentar explícitamente:

1. **Filtro de atípicos SIATA:** Valores `−999` (estaciones en mantenimiento) → `NULL`. Valores `PM2.5 < 0` → `NULL`.
2. **Eliminación de duplicados:** `df.drop_duplicates()` en cada dataset histórico.
3. **Validación de integridad referencial:** Consultas SQL que verifican registros huérfanos (`WHERE municipio_id IS NULL`).
4. **Normalización textual:** Diccionarios de estandarización para municipios y grupos de edad.
5. **Estrategia UPSERT:** `ON CONFLICT (estacion, fecha_hora) DO NOTHING` para evitar duplicados en la ingesta continua.

**Archivos de evidencia:**
- `backend/etl/extraccion/siata_api.py` — Filtro de negativos
- `backend/etl/transformacion/limpieza_riesgo.py` — Duplicados en `analisis_riesgo`
- `backend/etl/carga/siata.py` — UPSERT
- `backend/consultas/consultas_validacion.sql` L30-33 — Validación de huérfanos

#### 3.2.5 Reproducibilidad del pipeline (C2)

**Qué cambiar:** Agregar un párrafo o nota al pie que especifique:
- Versión de Python (3.8+) y librerías clave con versiones (ver `requirements.txt`).
- URL de la API SIATA consultada.
- Frecuencia de extracción (cada 2 minutos en producción, configurable en el scheduler).
- Motor de base de datos: PostgreSQL (Neon.tech en nube o local).

**Archivos de evidencia:**
- `backend/requirements.txt`
- `backend/etl/configuracion/settings.py` — URL de SIATA
- `backend/etl/scheduler.py` L59-66 — Configuración de frecuencia

---

### 3.3 Errores de edición y formato (C9, C10, C13, C14, C15, C16, C17, C18)

#### 3.3.1 Erratas textuales (C9)

| Ubicación en el paper | Error | Corrección |
|----------------------|-------|------------|
| Introducción, §3 (L33) | `2018y 2023` | `2018 y 2023` |
| Metodología, Extracción (L65) | `peticiones HTTP GET la API` | `peticiones HTTP GET a la API` |
| Metodología, Extracción (L65) | `epidemiológicos históricos (Fig. 2).` | `epidemiológicos históricos.` (eliminar referencia a Fig. 2 inexistente, o crear la figura correspondiente) |
| Metodología (L59) | `Fase 1. Exploración y transformación` (debería ser Fase 2) | `Fase 2. Exploración y transformación de datos` |

#### 3.3.2 Reemplazo de la Figura 1 (C10)

**Acción:** Reemplazar la Figura 1 actual por una versión renderizada del diagrama de flujo ETL que ya existe en `backend/anexos/documentos/generados/diagrama_flujo.md`. Renderizar el Mermaid como imagen PNG/SVG e incluirla con leyenda: *"Figura 1. Diagrama de flujo del pipeline ETL de adquisición e integración de datos ambientales y epidemiológicos."*

#### 3.3.3 Referencia duplicada (C18)

**Acción:** Las referencias [4] y [7] son el mismo artículo de Sserunjogi et al. (2025). Eliminar una de las dos, renumerar las referencias restantes y actualizar las citas en el texto.

#### 3.3.4 Verificación de formato general (C13–C17)

| Requisito | Estado actual | Acción |
|-----------|--------------|--------|
| Tamaño carta, márgenes 2.5 cm, TNR 12pt, interlineado 1.5 | No verificable en .md (formato final debe ser Word) | Aplicar al generar .docx final |
| Figuras y tablas numeradas con leyenda | Tablas 1 y 2 presentes, pero sin leyenda correcta en todas; referencia a Fig. 2 inexistente | Renumerar y agregar leyendas |
| Estilo IEEE ([n]) | Ya se usa parcialmente; verificar consistencia | Revisión completa |
| ≥8 referencias citadas en texto | Hay 12 citas ([1]–[12]) pero ref. [12] no se cita en texto aparte de Metodología | Verificar que [12] se cite, y eliminar duplicada [4]/[7] |
| ≥4 refs últimos 5 años (2021–2026) | [1]=2020, [2]=2024, [4]/[7]=2025, [6]=2024, [8]=2022 → al menos 4 cumplen | Cumplido; documentar |

---

### 3.4 Apoyo gráfico y evidencia de resultados (C11, C12)

**Qué cambiar:** Agregar al paper:

1. **Diagrama de flujo ETL** (ya existe en `backend/anexos/documentos/generados/diagrama_flujo.md`): reemplaza la Figura 1 actual.

2. **Tabla/muestra de datos integrados:** Incluir un extracto de `backend/anexos/datos/integrados/datos_integrados.csv` (2,402 registros) como nueva tabla o figura, mostrando cómo convergen las 3 fuentes.

3. **Captura del dashboard:** El frontend está desplegado en `https://airwise-health.onrender.com`. Tomar capturas del:
   - Mapa de calor con estaciones SIATA y semáforo ICA.
   - Calculadora de riesgo con un ejemplo de consulta.
   - Gráficos de tendencias históricas.

4. **Documentación del pipeline:** Referenciar en el paper que el código fuente completo, los notebooks EDA y las consultas de validación están disponibles como anexos.

**Archivos de evidencia:**
- `backend/anexos/datos/integrados/datos_integrados.csv`
- `backend/anexos/notebooks/integracion_datos.ipynb`
- `backend/anexos/documentos/generados/resultado_integracion.md`
- `backend/anexos/notebooks/limpieza_AnalisisRiesgo.ipynb`
- Notebooks EDA por dataset: `backend/anexos/notebooks/EnfermedadesCalculadas_2008_2017.ipynb`, `backend/anexos/notebooks/Tasa_Mortalidad.ipynb`, `backend/anexos/notebooks/difsionescalculadas (2).ipynb`

> **Ejemplo de reescritura (párrafo para Resultados):**
>
> *"La Figura 2 muestra el diagrama entidad-relación del modelo de datos implementado en PostgreSQL. La Figura 3 presenta una captura del dashboard interactivo AireSalud, desplegado en producción, que expone tres secciones: (A) un mapa de calor con las lecturas de PM2.5 por estación SIATA con semáforo ICA, (B) una calculadora de riesgo epidemiológico personalizado por municipio, sexo y grupo etario, y (C) gráficos de tendencias históricas de morbilidad y mortalidad respiratoria (2008–2017)."*

---

### 3.5 Referencias (C15, C16, C17, C18)

**Acciones concretas:**

1. **Eliminar duplicado [4]/[7]:** Ambas son Sserunjogi et al. (2025). Conservar solo una (sugerir mantener la de línea 200–201 como [4]) y eliminar la segunda (línea 207). Renumerar [8]→[7], [9]→[8], [10]→[9], [11]→[10], [12]→[11] en todo el documento.

2. **Verificar referencia [12]:** En el paper se cita `[12]` en la frase sobre ETL. Confirmar que corresponde a una referencia real sobre metodología ETL. Actualmente hay 12 entradas pero la [12] no está claramente vinculada — **verificar si falta una referencia sobre ETL** (p. ej., Kimball & Ross, "The Data Warehouse Toolkit" u otra fuente sobre ETL). Si falta, agregar una referencia apropiada.

3. **Verificar cita [3]:** La referencia [3] (Xiao Tang et al.) no tiene año claro y su conexión con el texto es débil. Evaluar si se puede reemplazar por una referencia más directamente relevante al monitoreo de calidad del aire con pipelines de datos.

---

## 4. Brechas (lo que NO se puede resolver con lo existente)

| # | Brecha identificada | Propuesta para cubrirla |
|---|---------------------|------------------------|
| B1 | **Datos epidemiológicos actualizados (post-2017):** Los evaluadores señalan la asincronía temporal como limitación. No existen en el proyecto datos epidemiológicos recientes. | **Opción A:** Buscar en el portal de datos abiertos del AMVA o del INS si hay datasets más recientes disponibles. **Opción B:** Reconocer explícitamente la limitación en el paper y justificar la validez del enfoque con la argumentación de `backend/anexos/documentos/contexto/fundamentacion.md`. **Opción C:** Consultar datos de SISAIRE (mencionado en `backend/anexos/documentos/contexto/contexto.md` L4) para complementar con PM2.5 histórico por municipio. |
| B2 | **Integración de PurpleAir:** El objetivo original del proyecto (ver `backend/anexos/documentos/contexto/contexto.md` L15-18) incluía sensores PurpleAir, pero no se implementó. Esto se menciona solo como trabajo futuro en las conclusiones. | Mantener como trabajo futuro bien argumentado. Si se desea mejorar, se podría implementar un extractor básico de la API de PurpleAir (es JSON público) y documentarlo como prueba de concepto. |
| B3 | **Métricas de validación cuantitativa del pipeline:** Los evaluadores no lo piden explícitamente, pero el paper carece de métricas de completitud, latencia o calidad del pipeline (e.g., % de registros cargados vs. esperados, tasa de éxito de las peticiones HTTP). | Ejecutar las consultas de `backend/consultas/consultas_validacion.sql` y documentar los conteos resultantes (registros por tabla, huérfanos = 0) como evidencia en la sección de Resultados. |
| B4 | **Figura 2 referida en el texto pero inexistente:** Se cita `(Fig. 2)` en la fase de Extracción pero no existe. | **Opción A:** Eliminar la referencia a Fig. 2. **Opción B:** Crear una Figura 2 que muestre el flujo de extracción (petición HTTP → parseo KML → DataFrame → PostgreSQL), lo cual fortalecería el apoyo gráfico solicitado por el Evaluador 2. |
| B5 | **Referencia [12] sobre ETL:** Se cita `[12]` en el texto pero no es claro a qué referencia corresponde en la lista actual. | Verificar si hay una referencia faltante sobre metodología ETL. Si no existe, agregar una (p. ej., Kimball, R., "The Data Warehouse ETL Toolkit", Wiley, 2004 — o una más reciente). |

---

## 5. Orden de Ejecución Sugerido (Checklist)

Ordenado por prioridad e impacto, agrupando tareas que se pueden hacer en paralelo.

### Bloque 1 — Correcciones inmediatas (≈ 1.5 h)
- [ ] **C9** — Corregir las 4 erratas textuales (`2018y`, `GET la API`, `Fig. 2`, `Fase 1→2`)
- [ ] **C18** — Eliminar la referencia duplicada [4]/[7] y renumerar todas las citas
- [ ] **C14** — Verificar numeración secuencial de figuras y tablas; agregar leyendas faltantes

### Bloque 2 — Metodología (≈ 8 h)
- [ ] **C3** — Agregar párrafo de delimitación geográfica (10 municipios, ~23 estaciones, JOIN ILIKE)
- [ ] **C4** — Explicitar la estrategia de selección temporal (`DISTINCT ON ... ORDER BY fecha_hora DESC`)
- [ ] **C5** — Incluir tabla del modelo relacional (dimensiones vs. hechos con tipos de dato)
- [ ] **C6** — Documentar las 5 técnicas de calidad de datos y detección de atípicos
- [ ] **C2** — Agregar nota de reproducibilidad (versiones, URL API, frecuencia, motor BD)
- [ ] **C10** — Renderizar el diagrama Mermaid de `diagrama_flujo.md` como imagen y reemplazar la Figura 1

### Bloque 3 — Introducción y novedad (≈ 5 h)
- [ ] **C1** — Ampliar el planteamiento del problema con indicadores concretos (β, % incremento)
- [ ] **C7** — Añadir justificación de validez de coeficientes β históricos con PM2.5 actual
- [ ] **C8** — Explicitar el diferenciador (Índice de Riesgo Local personalizado vía API REST)

### Bloque 4 — Resultados y apoyo gráfico (≈ 3 h)
- [ ] **C11** — Agregar extracto de datos integrados, captura de la vista SQL y documentación del pipeline
- [ ] **C12** — Describir el dashboard interactivo AireSalud como resultado adicional
- [ ] **B3** — Ejecutar consultas de validación y reportar métricas de completitud
- [ ] **B4** — Crear Figura 2 (flujo de extracción) o eliminar la referencia

### Bloque 5 — Formato final (≈ 1.5 h)
- [ ] **C13** — Aplicar formato Word (carta, márgenes, TNR 12pt, interlineado 1.5)
- [ ] **C15** — Revisión completa del estilo IEEE en citas y referencias
- [ ] **C16** — Confirmar ≥8 referencias citadas en texto
- [ ] **C17** — Confirmar ≥4 referencias de últimos 5 años
- [ ] **B5** — Verificar/agregar referencia [12] sobre ETL

### Bloque 6 — Revisión final
- [ ] Lectura completa del paper corregido buscando coherencia narrativa
- [ ] Verificar que cada figura y tabla se cite correctamente en el texto
- [ ] Verificar que la numeración de referencias sea continua tras eliminar el duplicado
- [ ] Revisión ortográfica y de estilo final

---

> **Nota:** Este plan no modifica los archivos `documento_evaluado.md` ni `comentarios_evaluadores.md`. Todas las acciones se refieren a cambios que deben aplicarse al generar la versión mejorada del paper.
