# Metodología reescrita — Pipeline de adquisición e integración de datos ambientales y epidemiológicos

> **Propósito de este documento.** Sustituye la sección *Metodología* del paper
> `documento_evaluado.md`. Responde de forma explícita a las observaciones de los
> evaluadores sobre reproducibilidad, delimitación geográfica, función de
> agregación, estructura de datos y calidad de datos (C2–C6 del
> `plan_mejoramiento.md`).
>
> **No modifica** `documento_evaluado.md` ni `comentarios_evaluadores.md`; es la
> versión lista para trasladar al informe final.
>
> **Trazabilidad con el código:** cada decisión metodológica indica el módulo que
> la implementa en `backend/etl/`. La guía de explicación del código está en
> `guia_explicacion_codigo.md`.

---

## 1. Enfoque metodológico y alcance

Este trabajo es una investigación aplicada de carácter tecnológico, con enfoque
exploratorio, cuantitativo y descriptivo-experimental. Su propósito es diseñar,
implementar y validar un pipeline ETL que integre mediciones ambientales de
PM2.5 en tiempo real con registros epidemiológicos históricos del Valle de
Aburrá, para estimar un incremento de riesgo epidemiológico local y
personalizado.

El pipeline se implementó en Python y se organizó en tres fases reproducibles:

| Fase | Nombre | Entrada | Salida | Módulo |
|------|--------|---------|--------|--------|
| 1 | Extracción | API SIATA (KML) y 4 CSV históricos | DataFrames crudos | `etl/extraccion/`, `etl/transformacion/limpieza_*.py` |
| 2 | Transformación | DataFrames crudos | DataFrames limpios y normalizados | `etl/transformacion/` |
| 3 | Integración y carga | DataFrames limpios | Tablas PostgreSQL y vista materializada | `etl/carga/`, `etl/pipeline.py` |

La automatización de la fuente primaria se implementó con un daemon
(`etl/scheduler.py`) que reutiliza la misma lógica de extracción y carga.

---

## 2. Delimitación del estudio

### 2.1 Delimitación geográfica

El estudio se delimita a los **10 municipios del Área Metropolitana del Valle de
Aburrá (AMVA)**:

| # | Municipio | # | Municipio |
|---|-----------|---|-----------|
| 1 | Medellín | 6 | Caldas |
| 2 | Bello | 7 | Copacabana |
| 3 | Envigado | 8 | La Estrella |
| 4 | Itagüí | 9 | Girardota |
| 5 | Sabaneta | 10 | Barbosa |

La red SIATA aporta mediciones de **hasta 23 estaciones activas** en el feed KML
de PM2.5. La unidad de análisis espacial es el **municipio**, no la estación:
las estaciones son el instrumento de medición y se agregan al municipio
correspondiente. Esta decisión es la que permite cruzar la exposición ambiental
con los registros epidemiológicos, que están desagregados por municipio.

**Mecanismo de correspondencia estación–municipio.** El vínculo se realiza por
coincidencia textual normalizada sobre el nombre de la estación:

```sql
JOIN municipios m
  ON us.estacion ILIKE '%' || m.nombre_normalizado || '%'
```

Antes del JOIN, un diccionario (`MUNICIPIOS_MAPA`) estandariza las variantes
ortográficas de los CSV (`medellin` → `Medellín`, `itagui` → `Itagüí`,
`laestrella` → `La Estrella`, etc.). Así, una estación como
`MED-UPAR Tráfico Centro` se asocia con `Medellín`.

Cuando una estación no puede asociarse a un municipio, o cuando un municipio no
tiene estación activa, el sistema aplica un **respaldo regional**: usa el
promedio de la última lectura válida de todas las estaciones
(`AVG(pm25_ica)`), y lo declara explícitamente en la respuesta de la API
(`nota_estimacion`). Este respaldo evita que la calculadora de riesgo quede sin
respuesta y hace explícita la incertidumbre.

### 2.2 Delimitación temporal

| Fuente | Cobertura | Frecuencia |
|--------|-----------|------------|
| API SIATA (PM2.5) | Tiempo real | El sensor publica aproximadamente cada 2 minutos; el sistema consulta de forma programada |
| Análisis de Riesgo | 2008–2017 | Carga histórica única |
| Enfermedades Calculadas | 2008–2017 | Carga histórica única |
| Tasa de Mortalidad | 2008–2017 | Carga histórica única |
| Defunciones | 2008–2017 | Carga histórica única |

La asincronía entre los coeficientes históricos (2008–2017) y las mediciones
actuales no invalida el cálculo: los coeficientes β representan relaciones
biológicas exposición–respuesta estables en el tiempo, y su aplicación a
concentraciones actuales es el enfoque estándar de la epidemiología ambiental
(la OMS publica funciones exposición–respuesta que se reutilizan durante años).
Esta limitación se reconoce explícitamente en la sección de discusión.

---

## 3. Variables y estructura de datos

### 3.1 Fuentes de datos

| Fuente | Tipo | Formato | Variables principales |
|--------|------|---------|----------------------|
| API SIATA | Primaria (sensor) | KML/XML sobre HTTP | `estacion`, `pm25_ica`, `fecha_hora`, `latitud`, `longitud`, `categoria_ica` |
| AnalisisRiesgo | Secundaria (archivo) | CSV `;`, UTF-8-BOM | `beta`, `exponencial_beta`, `limite_inferior`, `limite_superior`, `porcentaje_incremento_riesgo`, `municipio`, `sexo`, `edad`, `grupo diagnóstico` |
| EnfermedadesCalculadas | Secundaria (archivo) | CSV `;`, UTF-8-BOM | `Municipio`, `Periodo`, `Sexo`, `Edad`, `Grupo`, `Capitulo`, `casos` |
| TasaMortalidad | Secundaria (archivo) | CSV `;`, UTF-8-BOM | `Municipio`, `Año`, `Capítulo`, `Sexo`, `TasaMortalidadAjustada` |
| DefunsionesCalculadas | Secundaria (archivo) | CSV `;`, UTF-8-BOM | `Municipio`, `Periodo`, `Sexo`, `Edad`, `Grupo`, `Muertes` |

### 3.2 Modelo relacional (esquema estrella)

El almacenamiento se organiza en **tablas de dimensión** (catálogos compartidos)
y **tablas de hechos** (datos medidos), con el fin de evitar redundancia y
garantizar integridad referencial.

| Tipo | Tabla | Campos clave | Tipos | Relaciones |
|------|-------|--------------|-------|------------|
| Dimensión | `municipios` | `id`, `nombre`, `nombre_normalizado` | `SERIAL`, `VARCHAR` | FK en todas las tablas de hechos |
| Dimensión | `contaminantes` | `id`, `nombre`, `nombre_display` | `SERIAL`, `VARCHAR` | FK en `analisis_riesgo` |
| Dimensión | `grupos_diagnosticos` | `id`, `codigo_cie10`, `nombre`, `capitulo` | `SERIAL`, `VARCHAR` | FK en hechos de salud |
| Hecho | `analisis_riesgo` | `municipio_id`, `grupo_diagnostico_id`, `contaminante_id`, `beta`, `porcentaje_incremento_riesgo`, `sexo`, `grupo_edad` | `INT`, `NUMERIC`, `VARCHAR` | FK a 3 dimensiones |
| Hecho | `enfermedades` | `municipio_id`, `grupo_diagnostico_id`, `periodo`, `sexo`, `grupo_edad`, `casos` | `INT`, `VARCHAR` | FK a 2 dimensiones |
| Hecho | `tasa_mortalidad` | `municipio_id`, `anio`, `capitulo`, `sexo`, `tasa_ajustada` | `INT`, `VARCHAR`, `NUMERIC` | FK a `municipios` |
| Hecho | `defunciones` | `municipio_id`, `grupo_diagnostico_id`, `periodo`, `sexo`, `grupo_edad`, `muertes` | `INT`, `VARCHAR`, `NUMERIC` | FK a 2 dimensiones |
| Hecho | `mediciones_siata` | `estacion`, `pm25_ica`, `fecha_hora`, `latitud`, `longitud`, `categoria_ica`, `fecha_carga` | `VARCHAR`, `NUMERIC`, `TIMESTAMP` | `UNIQUE(estacion, fecha_hora)` |
| Vista | `vista_riesgo_integrado` | Campos cruzados SIATA + riesgo + municipios | — | JOIN de 4 tablas |

**Diccionario de variables clave del resultado integrado:**

| Campo | Tipo | Origen | Utilidad |
|-------|------|--------|----------|
| `municipio` | `VARCHAR` | Dimensión municipios | Delimitación territorial y filtro |
| `estacion_siata` | `VARCHAR` | API SIATA | Trazabilidad del sensor usado |
| `pm25_actual` | `NUMERIC` | API SIATA (última lectura) | Exposición actual |
| `categoria_ica` | `VARCHAR` | Clasificación Res. 2254 de 2017 | Semáforo de calidad del aire |
| `ultima_medicion` | `TIMESTAMP` | API SIATA | Frescura del dato |
| `coeficiente_riesgo` (`beta`) | `NUMERIC` | AnalisisRiesgo | Parámetro exposición–respuesta |
| `sexo`, `grupo_edad` | `VARCHAR` | AnalisisRiesgo | Desagregación poblacional |
| `incremento_basico_historico` | `NUMERIC` | AnalisisRiesgo | Riesgo de referencia |
| `incremento_riesgo_pct_actual` | `NUMERIC` | Cálculo derivado | Riesgo con PM2.5 actual |

El DDL completo se encuentra en `backend/etl/carga/esquema.py`.

---

## 4. Fase 1 — Extracción

### 4.1 Fuente primaria: API SIATA

- **Endpoint:** `https://www.siata.gov.co/kml/01_Redes/AMVARedAire/RedAireAMVA_PM25.kml`
- **Protocolo:** petición HTTP `GET` con `requests` y tiempo límite de 15 s.
- **Formato:** XML/KML; se eliminan los *namespaces* para simplificar el parseo
  con `xml.etree.ElementTree`.
- **Unidad de extracción:** cada `<Placemark>` representa una estación.
- **Campos extraídos:** `name` (estación), `ICA_PM25_Valor` (PM2.5),
  `fecha_ultima_actualizacion`, y `<coordinates>` (longitud, latitud).
- **Frecuencia:** el sensor publica aproximadamente cada 2 minutos. El pipeline
  completo se ejecuta una vez; el daemon `etl/scheduler.py` actualiza la fuente
  primaria cada hora en producción (`--demo` cada 10 s para demostración).

Cada lectura se clasifica con los puntos de corte de PM2.5 de la Resolución 2254
de 2017 (Tabla No. 6). Aunque la norma define estos rangos para promedios de
24 horas, el sistema los aplica a la lectura instantánea como aproximación
operativa:

| PM2.5 (µg/m³) | Categoría ICA |
|---------------|---------------|
| 0–12 | Buena |
| 13–37 | Aceptable |
| 38–55 | Dañina a la salud de grupos sensibles |
| 56–150 | Dañina para la salud |
| 151–250 | Muy dañina para la salud |
| 251–500 | Peligrosa |
| >500 | Peligrosa (fuera de la escala ICA) |

### 4.2 Fuentes secundarias: archivos CSV

Los cuatro archivos se leen con `pandas.read_csv(sep=';', encoding='utf-8-sig')`
desde `backend/anexos/datos/crudos/`. Son cargas históricas únicas y controladas.

---

## 5. Fase 2 — Transformación y calidad de datos

### 5.1 Transformaciones aplicadas

1. **Filtro por contaminante:** en `AnalisisRiesgo` se conservan solo registros de
   PM2.5 (`nombre contaminante == 'pm25'`), descartando PM10 y O₃ del cálculo de
   riesgo.
2. **Limpieza textual:** `strip()` en columnas categóricas; eliminación de
   espacios y mayúsculas inconsistentes.
3. **Conversión numérica:** reemplazo de coma decimal por punto
   (`'12,5' → 12.5`) y conversión a `float`/`int` en betas, tasas, casos y
   muertes.
4. **Normalización de municipios:** `MUNICIPIOS_MAPA` unifica variantes
   ortográficas a los 10 nombres oficiales del AMVA.
5. **Normalización de grupos de edad:** `EDADES_MAPA` unifica variantes a
   categorías epidemiológicas comunes.
6. **Renombrado a `snake_case`:** columnas finales consistentes con PostgreSQL.
7. **Columnas derivadas para visualización:** normalización Min-Max de variables
   numéricas (beta, muertes, tasas) para gráficos del dashboard. Estas columnas
   **no** se usan en el cálculo de riesgo ni se cargan como variables
   analíticas.

### 5.2 Técnicas de detección de atípicos y calidad de datos

| Técnica | Regla | Implementación |
|---------|-------|----------------|
| Valores de mantenimiento | `-999` y cualquier PM2.5 `< 0` → `NULL` | `etl/extraccion/siata_api.py` |
| Duplicados | `drop_duplicates()` por dataset histórico | `etl/transformacion/limpieza_*.py` |
| Atípicos extremos | PM2.5 `> 500 µg/m³` se reporta para revisión | `etl/transformacion/calidad_datos.py` |
| Integridad referencial | Verificación de registros huérfanos (`municipio_id IS NULL`) | `backend/consultas/consultas_validacion.sql` |
| Consistencia textual | Validación de municipios contra `MUNICIPIOS_MAPA` | `etl/transformacion/calidad_datos.py` |
| Idempotencia | `UPSERT`/`ON CONFLICT DO NOTHING` en ingesta continua | `etl/carga/siata.py` |
| Deduplicación temporal | `UNIQUE(estacion, fecha_hora)` | `etl/carga/esquema.py` |

La función `validar_calidad_datos()` se ejecuta al final de la transformación y
reporta dimensiones, nulos por columna, duplicados y tipos de dato. Se
complementa con las consultas SQL de validación y con `backend/check_data.py`.

---

## 6. Fase 3 — Integración y carga

### 6.1 Función de agregación espacial

La integración geográfica **no promedia estaciones**: asigna cada estación a un
municipio y, si hay varias estaciones en un mismo municipio, selecciona la
medición más reciente entre ellas:

```sql
SELECT DISTINCT ON (m.id)
    m.id, m.nombre_normalizado, us.estacion,
    us.pm25_ica, us.categoria_ica, us.fecha_hora
FROM ultima_siata us
JOIN municipios m
  ON us.estacion ILIKE '%' || m.nombre_normalizado || '%'
ORDER BY m.id, us.fecha_hora DESC
```

Este `DISTINCT ON (m.id) ... ORDER BY m.id, fecha_hora DESC` selecciona, para
cada municipio, la lectura válida más reciente entre sus estaciones.

### 6.2 Función de agregación temporal (decisión explícita)

**No se aplica promedio, suma ni mediana sobre las lecturas de alta frecuencia
para el cálculo de riesgo.** La estrategia es seleccionar la **observación más
reciente por estación**:

```sql
WITH ultima_siata AS (
    SELECT DISTINCT ON (estacion)
        estacion, pm25_ica, categoria_ica, fecha_hora
    FROM mediciones_siata
    WHERE pm25_ica IS NOT NULL
    ORDER BY estacion, fecha_hora DESC
)
```

**Justificación:** el objetivo es estimar el riesgo con la exposición instantánea
actual, no describir una tendencia histórica del sensor. Un promedio de 15
minutos introduciría suavización y retrasaría la señal de alerta.

La única función de agregación que se usa es `AVG(pm25_ica)` como **respaldo
regional** cuando un municipio no tiene estación asociada; en ese caso la API lo
declara en `nota_estimacion`. La normalización Min-Max (Fase 2) es solo para
visualización y no interviene en el cálculo.

### 6.3 Cálculo del riesgo

El incremento porcentual de riesgo se calcula con la función exposición-respuesta
para un incremento de 10 µg/m³ de PM2.5:

```
ΔR = (e^(β · PM2.5_actual / 10) − 1) × 100
```

donde `β` es el coeficiente epidemiológico del municipio, sexo, grupo etario y
diagnóstico CIE-10. Se calcula en la vista materializada
(`etl/carga/vista_integrada.py`) y en la calculadora de la API
(`backend/app/routers/salud.py`), que además aplica respaldos explícitos cuando
faltan coeficientes para una combinación demográfica.

### 6.4 Estrategias de carga

| Dato | Estrategia | Motivo |
|------|-----------|--------|
| Históricos (4 CSV) | `TRUNCATE` + `INSERT` por lotes | Recarga limpia e idempotente; evita acumulación de duplicados |
| SIATA (tiempo real) | `INSERT ... ON CONFLICT (estacion, fecha_hora) DO NOTHING` | Ingesta continua sin duplicados |
| Dimensiones | `INSERT ... ON CONFLICT DO NOTHING` | Catálogos estables |
| Vista integrada | `CREATE MATERIALIZED VIEW IF NOT EXISTS` / `REFRESH` | Evita recalcular el JOIN en cada consulta |

La carga masiva usa `psycopg2.extras.execute_values` por lotes.

### 6.5 Vista materializada integrada

`vista_riesgo_integrado` une cuatro relaciones:

```
mediciones_siata → municipios → analisis_riesgo → grupos_diagnosticos
```

y produce una fila por combinación municipio × estación × enfermedad × sexo ×
grupo etario, con el PM2.5 actual y el incremento de riesgo calculado. Es la
evidencia concreta de que las tres fuentes convergen en un solo esquema.

---

## 7. Reproducibilidad

### 7.1 Requisitos y versiones

- **Lenguaje:** Python 3.12 o superior (`backend/pyproject.toml`).
- **Librerías mínimas:** `pandas>=2.0`, `requests>=2.31`, `psycopg2-binary>=2.9`,
  `python-dotenv>=1.0`, `schedule>=1.2`, `fastapi>=0.115`,
  `uvicorn[standard]>=0.30` (`backend/requirements.txt`).
- **Base de datos:** PostgreSQL 14 o superior, local o en la nube
  (Neon.tech/Render).
- **Configuración:** variable de entorno `DATABASE_URL` (nube) o `DB_HOST`,
  `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` (local). No hay credenciales
  embebidas en el código; se leen con `python-dotenv`.

### 7.2 Ejecución reproducible

Desde la carpeta `backend/`:

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Pipeline ETL completo (extracción + transformación + carga)
python -m etl.pipeline

# 3. Actualización periódica de la fuente primaria
python -m etl.scheduler          # producción: cada 1 hora
python -m etl.scheduler --demo   # demostración: cada 10 segundos
```

### 7.3 Idempotencia y determinismo

- El DDL usa `IF NOT EXISTS`; las dimensiones usan `ON CONFLICT DO NOTHING`.
- Los históricos se recargan con `TRUNCATE` + `INSERT`, por lo que ejecutar el
  pipeline dos veces produce el mismo estado.
- La ingesta SIATA usa `ON CONFLICT (estacion, fecha_hora) DO NOTHING`.
- Los diccionarios de normalización son deterministas y versionados en el
  repositorio.
- La única fuente de variación esperada es la lectura del sensor en tiempo real.

### 7.4 Verificación

| Verificación | Comando / archivo | Resultado esperado |
|--------------|-------------------|--------------------|
| Conteo por tabla | `backend/check_data.py` | Registros cargados coherentes con los CSV |
| Integridad referencial | `backend/consultas/consultas_validacion.sql` | Cero registros huérfanos |
| Estado del pipeline | Salida de `python -m etl.pipeline` | Mensajes `[OK]` por cada fase |
| Vista integrada | Consulta a `vista_riesgo_integrado` | Filas con `pm25_actual` e `incremento_riesgo_pct_actual` |

Volúmenes de referencia documentados en el proyecto: 1.652 registros de análisis
de riesgo, 713 de tasa de mortalidad y las series de morbilidad y defunciones
2008–2017 de los 10 municipios del AMVA.

---

## 8. Relación de la metodología con la investigación

- **Problema:** la información ambiental (SIATA) y la epidemiológica (AMVA) están
  fragmentadas, y el ICA genérico no traduce la exposición en riesgo de salud.
- **Objetivo:** integrar ambas dimensiones en un esquema relacional reproducible
  y exponer un Índice de Riesgo Local personalizado por municipio, sexo, grupo
  etario y diagnóstico CIE-10.
- **Aporte metodológico:** el pipeline no solo limpia y almacena datos; define un
  vínculo geográfico explícito (estación→municipio), una regla temporal explícita
  (última lectura por estación) y una función de riesgo explícita
  (`ΔR = (e^(β·PM2.5/10) − 1) × 100`). Esa cadena de decisiones es lo que hace
  el resultado auditable y reproducible.
- **Novedad:** integraciones previas se centran en índices ambientales genéricos;
  aquí se cruza la exposición actual con coeficientes epidemiológicos
  desagregados y se expone el riesgo personalizado vía API REST.

---

## 9. Limitaciones

1. Los datos epidemiológicos disponibles cubren 2008–2017; se justifica el uso de
   β históricos por su estabilidad biológica, pero se reconoce como limitación.
2. La correspondencia estación–municipio depende de la calidad del nombre de la
   estación; se mitiga con normalización y respaldo regional.
3. El respaldo regional es una aproximación cuando no hay estación local y se
   informa explícitamente al usuario.
4. No se implementó todavía la ingesta de sensores ciudadanos PurpleAir; se
   plantea como trabajo futuro.

---

## 10. Trazabilidad con las observaciones de los evaluadores

| Comentario | Requerimiento | Sección de esta metodología |
|------------|---------------|------------------------------|
| C2 | Metodología 100 % reproducible | §7 (versiones, comandos, idempotencia, verificación) |
| C3 | Delimitación geográfica e integración estación–municipio | §2.1, §6.1 |
| C4 | Función de agregación explícita | §6.2 (decisión: última lectura, no promedio; `AVG` solo como respaldo) |
| C5 | Estructura de datos de las variables | §3.1 y §3.2 (diccionario y modelo relacional) |
| C6 | Atípicos y calidad de datos | §5.2 |
| C1/C7/C8 | Indicadores, validez temporal y novedad | §2.2, §8 |
| C11 | Evidencia del resultado integrado | §6.5 y §7.4 |

---

## Anexo — Pseudocódigo del pipeline

```text
INICIO
  crear_base_de_datos_si_no_existe()
  crear_esquema()                        # DDL idempotente

  # Fase 1 y 2
  df_riesgo       = limpiar_analisis_riesgo()     # filtra PM2.5, normaliza, deduplica
  df_enfermedades = limpiar_enfermedades()
  df_mortalidad   = limpiar_tasa_mortalidad()
  df_defunciones  = limpiar_defunciones()
  validar_calidad_datos(df_*)                     # nulos, duplicados, tipos

  # Fase 3
  poblar_dimensiones_basicas()                    # PM10, PM2.5, O3
  municipios, diagnosticos = asegurar_catalogos(df_*)
  vaciar_tablas_hechos()
  cargar_hechos(df_*, municipios, diagnosticos)   # TRUNCATE + INSERT
  df_siata = extraer_siata()                      # HTTP GET KML, filtra -999
  cargar_mediciones_siata(df_siata)               # UPSERT
  crear_o_refrescar_vista_integrada()             # JOIN + cálculo ΔR

FIN
```
