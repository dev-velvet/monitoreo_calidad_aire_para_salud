# Análisis exploratorio de la API de Calidad del Aire de Colombia

**Dataset:** `g4t8-zkc3` — *Calidad del Aire en Colombia* (IDEAM / SISAIRE, datos.gov.co)  
**Proyecto:** Monitoreo de calidad del aire para salud — Valle de Aburrá  
**Consulta realizada:** 2026-11-02  
**Corte temporal de los datos:** 2020-01-01 a 2025-12-31  
**Alcance de este documento:** conexión a la API, perfilamiento, calidad de datos, análisis exploratorio de PM2.5 en el Valle de Aburrá, indicadores de salud relacionados, evaluación de la meta de reducción del 49% al 2030 y fuentes complementarias verificadas para cerrar brechas 2015–2025.

---

## 1. Resumen ejecutivo

1. La API es **abierta, no requiere token** y entrega datos en JSON/CSV/XML mediante SoQL (Socrata). El dataset tiene **18 campos** y **4.583.670 registros de PM2.5** a nivel nacional.
2. Para el Valle de Aburrá (10 municipios) hay **1.203.202 registros de PM2.5** entre 2020 y 2025, medidos por **30 a 32 estaciones** por año, principalmente con frecuencia horaria (`duraci_n = 60` minutos).
3. **Hallazgo crítico de calidad:** entre 2020 y 2023 varias estaciones del AMVA reportaron PM2.5 con un **desplazamiento de escala (×10 o ×100)**. Sin corregir, los promedios anuales llegan a 455–633 µg/m³; corregidos quedan en **13,8–18,3 µg/m³**, consistentes con 2024–2025. Cualquier análisis histórico debe corregir o marcar estos registros.
4. Con la serie corregida, el promedio regional anual es **~15,8 µg/m³** y se mantiene **prácticamente plano entre 2020 y 2025** (sin tendencia descendente clara). Está por debajo de la norma colombiana anual (25 µg/m³) y de la meta PIGECA 2030 (23 µg/m³), pero **muy por encima de la guía anual de la OMS 2021 (5 µg/m³)**.
5. La exposición aguda sigue siendo relevante: en 2024–2025, **51,6% de los días-estación superaron 15 µg/m³** (guía OMS 24 h), **12,0% superaron 25 µg/m³** y **0,1% superaron 50 µg/m³** (norma colombiana 24 h).
6. El dataset **no contiene variables de salud, población ni emisiones**. Los CSV del proyecto cubren salud 2008–2017, pero se verificaron fuentes oficiales que permiten extender el análisis: IDEAM publica PM2.5 anual por estación 2007–2024; DANE, población municipal 2018–2042 y defunciones 2024–2025; la Secretaría de Salud de Antioquia, morbilidad municipal 2019–2024; y AMVA/EPM, inventarios de emisiones 2015/2016 y 2018. Con esto hay **solapamiento parcial 2020–2023** (aire, morbilidad y población) y **2024–2025** (aire y mortalidad por IRA), pero la relación causal sigue requiriendo los **coeficientes beta** de `AnalisisRiesgo` (392 modelos PM2.5) y un diseño de estudio adecuado; no basta una correlación simple.
7. Sobre la meta del **−49% de emisiones al 2030**: el PIGECA proyecta **915 t/año de PM2.5** en 2030, lo que equivale a ~49% menos frente a la línea base 2015 (~1.795 t/año). El inventario oficial 2015/2016 suma **~1.830 t/año** (1.496 móviles + 334 fijas), consistente con esa línea base. La actualización 2018, según una síntesis secundaria, habría subido a **~2.873 t/año** (2.625 móviles + 248 fijas), lo que haría la meta más exigente; debe confirmarse con el informe primario AMVA/UPB. Este dataset **no mide emisiones**, solo concentraciones, y **no cubre 2015–2019**. En concentración, el nivel corregido de 2025 (~14,8 µg/m³) ya está por debajo del equivalente de −49% frente a 2015 (16,8 µg/m³) y de la meta PIGECA (23 µg/m³); sin embargo, la tendencia 2020–2025 es plana y no soporta una reducción adicional del 49% frente al nivel actual (7,5 µg/m³). La verificación de emisiones requiere los inventarios primarios y la serie 2015–2019.
8. **Fuentes complementarias verificadas (sección 8):** el PM2.5 histórico 2015–2019 existe en IDEAM, pero no es una serie regional homogénea (2015–2017 con 6–10 estaciones; 2019 con solo 2). La morbilidad respiratoria municipal 2019–2023 muestra 1,11 → 0,53 → 0,38 → 1,28 → 1,45 millones de consultas, con el mínimo en 2021 por COVID-19; el archivo 2024 está incompleto y no debe usarse para tendencia. Las muertes por IRA en 2024–2025 fueron 1.132 y 1.331 (27,2 y 31,7 por 100.000), un indicador de validación, no una prueba causal.

---

## 2. Conexión a la API

### 2.1 Ficha técnica del endpoint

| Atributo | Valor |
|---|---|
| URL base (JSON) | `https://www.datos.gov.co/resource/g4t8-zkc3.json` |
| URL base (CSV) | `https://www.datos.gov.co/resource/g4t8-zkc3.csv` |
| ID Socrata | `g4t8-zkc3` |
| Entidad | IDEAM — Subsistema de Información sobre Calidad del Aire (SISAIRE) |
| Autenticación | No requiere. Token de aplicación opcional para mayores límites de uso |
| Lenguaje de consulta | SoQL (Socrata Query Language) |
| Límite por petición | 50.000 filas (`$limit=50000`); paginar con `$offset` |
| Formatos | JSON, CSV, XML |
| Cobertura | Nacional, 2020-01-01 a 2025-12-31 |

**Parámetros SoQL útiles:**

| Parámetro | Uso |
|---|---|
| `$select` | Columnas y agregaciones (`avg`, `count`, `min`, `max`, `sum`, `substring`) |
| `$where` | Filtros. Ejemplo: `msfl_code='PM2.5' AND departamento='Antioquia'` |
| `$group` | Agrupaciones (año, mes, estación, municipio) |
| `$order` | Ordenamiento |
| `$limit` / `$offset` | Paginación |
| `$q` | Búsqueda de texto completo (poco útil aquí) |

> Nota: `med_fecha_inicio` y `med_fecha_final` están almacenados como **texto**, no como fecha. Por eso las agregaciones temporales se hacen con `substring(med_fecha_inicio,1,4)` (año) o `substring(med_fecha_inicio,1,7)` (mes), y en Python con `pd.to_datetime()`.

### 2.2 Ejemplo de consulta directa

```bash
curl -s "https://www.datos.gov.co/resource/g4t8-zkc3.json?\$where=msfl_code='PM2.5'%20AND%20departamento='Antioquia'&\$limit=5"
```

### 2.3 Conexión reproducible en Python

```python
import requests
import pandas as pd

BASE_URL = "https://www.datos.gov.co/resource/g4t8-zkc3.json"

MUNICIPIOS_VA = [
    "Medellín", "Bello", "Itagüí", "Envigado", "Sabaneta",
    "Caldas", "La Estrella", "Copacabana", "Girardota", "Barbosa",
]


def consultar(where: str, select: str = "*", limit: int = 50000, offset: int = 0):
    params = {
        "$select": select,
        "$where": where,
        "$limit": limit,
        "$offset": offset,
        "$order": "med_fecha_inicio",
    }
    respuesta = requests.get(BASE_URL, params=params, timeout=60)
    respuesta.raise_for_status()
    return respuesta.json()


def descargar_pm25_valle_aburra(desde="2024-01-01", hasta="2026-01-01"):
    municipios = ",".join(f"'{m}'" for m in MUNICIPIOS_VA)
    where = (
        "msfl_code='PM2.5' AND departamento='Antioquia' "
        f"AND municipio in({municipios}) "
        f"AND med_fecha_inicio >= '{desde}' "
        f"AND med_fecha_inicio < '{hasta}'"
    )
    filas, offset = [], 0
    while True:
        bloque = consultar(where=where, limit=50000, offset=offset)
        if not bloque:
            break
        filas.extend(bloque)
        if len(bloque) < 50000:
            break
        offset += 50000

    df = pd.DataFrame(filas)
    df["med_fecha_inicio"] = pd.to_datetime(df["med_fecha_inicio"])
    df["med_concentracion_estandar"] = pd.to_numeric(
        df["med_concentracion_estandar"], errors="coerce"
    )
    return df


if __name__ == "__main__":
    df = descargar_pm25_valle_aburra()
    print(df.shape)
    print(df[["municipio", "nombre_est", "med_fecha_inicio", "med_concentracion_estandar"]].head())
```

### 2.4 Consultas SoQL usadas en este análisis

**Serie anual (primero por estación, luego promedio entre estaciones):**

```text
$select=substring(med_fecha_inicio,1,4) as anio,estacion_id,nombre_est,municipio,avg(med_concentracion_estandar) as prom,count(*) as n
$where=msfl_code='PM2.5' AND departamento='Antioquia' AND municipio in('Medellín','Bello','Itagüí','Envigado','Sabaneta','Caldas','La Estrella','Copacabana','Girardota','Barbosa')
$group=anio,estacion_id,nombre_est,municipio
$order=anio
```

> Esta consulta devuelve una fila por estación-año. La serie regional se obtiene promediando esas filas en Python. Así se evita que una estación con más registros domine el promedio. Antes de promediar 2020–2023, aplicar la corrección de escala descrita en la sección 4.1.

**Serie mensual:**

```text
$select=substring(med_fecha_inicio,1,7) as mes,municipio,nombre_est,avg(med_concentracion_estandar) as prom,count(*) as n
$where=msfl_code='PM2.5' AND departamento='Antioquia' AND duraci_n=60 AND med_fecha_inicio>='2024-01-01' AND municipio in('Medellín','Bello','Itagüí','Envigado','Sabaneta','Caldas','La Estrella','Copacabana','Girardota','Barbosa')
$group=mes,municipio,nombre_est
$order=mes
```

> La tabla mensual se obtiene promediando en Python las medias mensuales por estación, para no sobrerrepresentar estaciones con más datos.

**Ranking de estaciones (datos horarios):**

```text
$select=nombre_est,municipio,avg(med_concentracion_estandar) as prom,count(*) as n
$where=msfl_code='PM2.5' AND departamento='Antioquia' AND duraci_n=60 AND med_fecha_inicio>='2025-01-01' AND med_fecha_inicio<'2026-01-01' AND municipio in(...)
$group=nombre_est,municipio
$order=prom desc
```

**Excedencias diarias (agregar hora a día):**

```text
$select=substring(med_fecha_inicio,1,10) as dia,municipio,nombre_est,avg(med_concentracion_estandar) as prom,count(*) as horas
$where=msfl_code='PM2.5' AND departamento='Antioquia' AND duraci_n=60 AND med_fecha_inicio>='2024-01-01' AND med_fecha_inicio<'2026-01-01' AND municipio in(...)
$group=dia,municipio,nombre_est
$order=dia
$limit=50000
```

> La consulta anterior entrega el promedio diario por estación. En Python se filtran los días con `horas >= 18` y se cuentan los que superan 15, 25 o 50 µg/m³. No se debe usar `duraci_n=1440` para este cálculo: en este dataset hay muy pocos registros diarios y no cubren todas las estaciones.

---

## 3. Descripción y diccionario del dataset

### 3.1 Diccionario de campos

| Campo | Tipo | Descripción | Uso recomendado en el proyecto |
|---|---|---|---|
| `estacion_id` | texto | Código de la estación | Dimensión estación; llave para series por estación |
| `nombre_fgda` | texto | Autoridad ambiental que reporta (AMVA, CORANTIOQUIA, CORNARE) | Filtrar red de monitoreo y evaluar cobertura |
| `nombre_est` | texto | Nombre de la estación | Visualización, mapas y cruce con SIATA |
| `msfl_code` | texto | Código del contaminante o variable (`PM2.5`, `PM10`, `NO2`, etc.) | Filtro principal y dimensión contaminante |
| `med_concentracion_estandar` | numérico | Concentración medida | Variable de hecho; requiere validación de escala |
| `med_fecha_inicio` | texto | Fecha/hora inicial del intervalo | Dimensión tiempo; parsear a fecha |
| `med_fecha_final` | texto | Fecha/hora final del intervalo | Control de duración y solapamientos |
| `latitud` | texto | Latitud de la estación | Mapa y cruce espacial con municipio |
| `longitud` | texto | Longitud de la estación | Mapa y cruce espacial con municipio |
| `altitud` | numérico | Altitud de la estación (m s. n. m.) | Covariable espacial/ambiental |
| `nombre_unidad` | texto | Nombre de la unidad (`Microgramos por metro cúbico`) | Validar unidades antes de agregar |
| `sigla_unidad` | texto | Sigla (`ug/m3`) | Validar unidades antes de agregar |
| `duraci_n` | numérico | Duración del intervalo en minutos (60 = horario; 1440 = diario) | Define si el dato es horario o diario; base para agregación |
| `codigo_departamento` | numérico | Código DANE del departamento | Filtro Antioquia (05) |
| `departamento` | texto | Nombre del departamento | Filtro |
| `codigo_municipio` | texto | Código DANE del municipio | Llave de integración con salud |
| `municipio` | texto | Nombre del municipio | Llave de integración con salud |
| `tipo_estacion` | texto | `Fija` o `Indicativa` | Filtrar estaciones de referencia vs indicativas |

### 3.2 Contaminantes y variables disponibles

| `msfl_code` | Variable | Registros nacionales | Relevancia para el proyecto |
|---|---|---:|---|
| `PM2.5` | Material particulado fino | 4.583.670 | **Contaminante priorizado** por su impacto respiratorio y cardiovascular |
| `PM10` | Material particulado grueso | 3.936.509 | Fracción gruesa; útil para comparar y como precursora |
| `NO2` | Dióxido de nitrógeno | 1.747.285 | Tráfico vehicular; precursor de PM2.5 secundario |
| `O3` | Ozono | 1.877.251 | Contaminante secundario; afecta vías respiratorias |
| `SO2` | Dióxido de azufre | 1.834.858 | Fuentes fijas/industriales; precursor de PM2.5 |
| `CO` | Monóxido de carbono | 1.431.029 | Combustión; indicador de tráfico |
| `VViento` | Velocidad del viento | 3.841.841 | Dispersión de contaminantes |
| `DViento` | Dirección del viento | 3.803.788 | Transporte de contaminantes |
| `TAire10` / `TAire2` | Temperatura del aire | 2.270.684 / 1.835.251 | Covariable meteorológica |
| `HAire10` / `HAire2` | Humedad del aire | 1.887.163 / 1.578.408 | Covariable; afecta sensores ópticos |
| `PLiquida` | Precipitación líquida | 3.322.035 | Lavado atmosférico |
| `P` | Presión atmosférica | 3.097.426 | Covariable meteorológica |
| `RGlobal` | Radiación global | 1.520.459 | Covariable; fotólisis de ozono |
| `RUVb` | Radiación UV-B | 255.554 | Covariable |
| `PST` | Partículas suspendidas totales | 80 | Cobertura marginal; no usar |

> Para el proyecto, el núcleo es **PM2.5**; `PM10`, `NO2`, `O3`, `SO2` y `CO` sirven como co-contaminantes y las variables meteorológicas como confusores o para modelos de dispersión.

### 3.3 Cobertura del dataset

| Ámbito | Registros PM2.5 | Estaciones (2024–2025) | Período |
|---|---:|---:|---|
| Colombia | 4.583.670 | — | 2020-01-01 a 2025-12-31 |
| Antioquia | 1.316.867 | — | 2020-01-01 a 2025-12-31 |
| Valle de Aburrá (10 municipios) | 1.203.202 | 30–32 por año (45 con algún dato) | 2020-01-01 a 2025-12-31 |

**Registros de PM2.5 en el Valle de Aburrá por año:**

| Año | Registros | Estaciones |
|---|---:|---:|
| 2020 | 180.829 | 30 |
| 2021 | 201.793 | 31 |
| 2022 | 210.458 | 32 |
| 2023 | 201.615 | 31 |
| 2024 | 203.243 | 31 |
| 2025 | 205.264 | 30 |

La frecuencia dominante es **horaria** (`duraci_n = 60` en 1.308.552 registros de Antioquia), con muy pocos registros diarios (`duraci_n = 1440` en 1.387 registros). Por lo tanto, para analizar excedencias diarias hay que **agregar la hora a día** y exigir un mínimo de horas válidas.

---

## 4. Análisis exploratorio de PM2.5 en el Valle de Aburrá

### 4.1 Calidad de datos

| Revisión | Resultado |
|---|---|
| Nulos en `med_concentracion_estandar` (Antioquia, PM2.5) | 0 |
| Nulos en latitud/longitud | 0 |
| Nulos en municipio | 0 |
| Valores ≤ 0 (Antioquia, PM2.5) | 4.509 (0,34%) |
| Valores ≤ 0 en 2024–2025 | 15 |
| Unidad reportada | `Microgramos por metro cúbico` (`ug/m3`) en todos los años |
| Cobertura horaria | Alta y continua; 30–32 estaciones activas por año |

**Problema de escala 2020–2023.** Al comparar cada estación-año con su propio nivel de 2024–2025 (período consistente), se observan ratios de ~10 o ~100 en varias estaciones del AMVA. Ejemplos:

| Año | Estación | Promedio reportado (µg/m³) | Referencia 2024–2025 (µg/m³) | Ratio | Factor probable |
|---|---|---:|---:|---:|---:|
| 2021 | ALTAVISTA (Medellín) | 1.005,6 | 21,3 | 47,3 | ÷100 |
| 2022 | ALTAVISTA (Medellín) | 1.631,1 | 21,3 | 76,6 | ÷100 |
| 2023 | ALTAVISTA (Medellín) | 1.492,2 | 21,3 | 70,1 | ÷100 |
| 2020 | BIBLIOTECA FERNANDO B. (Medellín) | 131,7 | 15,4 | 8,5 | ÷10 |
| 2023 | POLITÉCNICO JIC (Medellín) | 1.673,0 (mediana) | 19,2 (mediana) | ~87 | ÷100 |
| 2024 | POLITÉCNICO JIC (Medellín) | 19,2 (mediana) | 19,2 | 1,0 | Sin corrección |

**Conteo de estaciones corregidas por año (método de referencia 2024–2025):**

| Año | Factor ×1 | Factor ÷10 | Factor ÷100 |
|---|---:|---:|---:|
| 2020 | 15 | 13 | 2 |
| 2021 | 16 | 0 | 15 |
| 2022 | 17 | 0 | 15 |
| 2023 | 15 | 1 | 15 |
| 2024 | 31 | 0 | 0 |
| 2025 | 30 | 0 | 0 |

> **Advertencia:** esta corrección es un **diagnóstico de calidad**, no una corrección oficial. Se recomienda contrastar con el AMVA/SISAIRE y conservar una bandera (`escala_sospechosa`) en la base de datos. El desplazamiento decimal puede deberse a cambios en el reporte, no a la concentración real.

### 4.2 Serie anual de PM2.5

| Año | Promedio reportado sin corregir (µg/m³) | Promedio corregido (µg/m³) | Factor promedio implícito |
|---|---:|---:|---:|
| 2020 | 154,2 | 17,1 | 9,0 |
| 2021 | 455,9 | 13,8 | 33,0 |
| 2022 | 632,6 | 15,7 | 40,3 |
| 2023 | 624,9 | 14,9 | 41,9 |
| 2024 | 18,3 | 18,3 | 1,0 |
| 2025 | 14,8 | 14,8 | 1,0 |

**Lectura:** la serie corregida es estable, con promedio **~15,8 µg/m³** y variación interanual de ~13,8 a 18,3 µg/m³. El valor de 2024 es el más alto del período corregido; 2025 baja a 14,8 µg/m³. No se observa una tendencia descendente sostenida: la pendiente lineal 2020–2025 es prácticamente plana (~+0,03 µg/m³ por año, influida por el pico de 2024). La serie regional se calcula como **promedio simple de las medias anuales por estación**, no como promedio ponderado por número de registros.

**Comparación con normas:**

| Referencia | Valor anual (µg/m³) | ¿Se cumple en 2025? |
|---|---:|---|
| OMS 2021 (guía anual) | 5 | No (14,8 ≈ 3× la guía) |
| Resolución 2254 de 2017 (norma anual) | 25 | Sí |
| PIGECA 2030 (meta anual) | 23 | Sí |
| Equivalente a −49% frente a 2015 (33 → 16,8) | 16,8 | Sí, por poco margen |

### 4.3 Estacionalidad mensual (2024–2025)

| Mes | Promedio 2024 (µg/m³) | Promedio 2025 (µg/m³) |
|---|---:|---:|
| Enero | 20,4 | 16,4 |
| Febrero | 19,8 | 18,6 |
| Marzo | 30,4 | 19,9 |
| Abril | 23,2 | 14,6 |
| Mayo | 14,3 | 14,0 |
| Junio | 13,0 | 12,6 |
| Julio | 14,1 | 12,4 |
| Agosto | 16,4 | 12,9 |
| Septiembre | 18,6 | 13,8 |
| Octubre | 15,6 | 13,9 |
| Noviembre | 13,8 | 14,0 |
| Diciembre | 16,9 | 16,3 |

**Patrón:** los mayores niveles se concentran en **febrero–abril** (temporada seca y transición), con un pico marcado en **marzo de 2024 (30,4 µg/m³)**. Los mínimos se dan en **junio–julio** (12–13 µg/m³). Este patrón es consistente con la climatología andina y con la menor dispersión/lluvia en la primera temporada seca. Para el proyecto, esto implica usar **promedios móviles** y **comparaciones mes a mes**, no solo promedios anuales.

### 4.4 Estaciones con mayores niveles en 2025

> Promedios calculados a partir de las mediciones horarias agregadas a día (≥18 h válidas) y luego promediadas en el año. No se usan los pocos registros nativos con `duraci_n=1440`.

| Estación | Municipio | Promedio 2025 (µg/m³) | Observación |
|---|---|---:|---|
| TRÁFICO CENTRO | Medellín | 23,8 | Estación de tráfico; el valor más alto |
| ITA-LGO | Medellín | 21,9 | Estación fija de CORANTIOQUIA |
| ALTAVISTA | Medellín | 19,3 | Estación fija |
| CASA JUSTICIA | Itagüí | 18,5 | Estación fija del AMVA |
| I.E. PEDRO JUSTO B. | Medellín | 18,3 | Estación fija |
| LA TABLAZA I.E JOSE ANTONIO GALAN | La Estrella | 18,0 | Estación fija |
| ALMACÉN GENERAL DE EPM | Medellín | 17,1 | Estación fija |
| I.E. CONCEJO MUNICIPAL | Itagüí | 16,5 | Estación fija |

Las estaciones de **tráfico** y las ubicadas en el **centro de Medellín** concentran los mayores niveles. Para el análisis de salud, conviene ponderar por población expuesta y no solo por estación.

### 4.5 Excedencias diarias y normas de 24 horas

Para este cálculo se agregaron las mediciones horarias a nivel diario por estación, exigiendo **≥18 horas válidas** por día. En 2024–2025 se obtuvieron **17.221 días-estación** válidos.

| Umbral | Días-estación que exceden | Porcentaje |
|---|---:|---:|
| > 15 µg/m³ (guía OMS 24 h, 2021) | 8.878 | 51,6% |
| > 25 µg/m³ (referencia intermedia) | 2.062 | 12,0% |
| > 50 µg/m³ (norma colombiana 24 h) | 10 | 0,1% |

| Indicador diario regional | Valor |
|---|---:|
| Mediana del promedio diario regional | 15,2 µg/m³ |
| Máximo del promedio diario regional | 43,1 µg/m³ |
| Días con promedio regional > 15 µg/m³ | 378 de 731 (51,7%) |
| Días con promedio regional > 25 µg/m³ | 54 de 731 (7,4%) |

**Lectura:** aunque el promedio anual cumple la norma colombiana y la meta PIGECA, **la exposición diaria sigue siendo alta**: más de la mitad de los días-estación superan la guía diaria de la OMS. La meta PIGECA de 24 h para 2030 es 15 µg/m³; con la mediana actual de 15,2 µg/m³, esa meta **no está cumplida** y es el frente más exigente.

---

## 5. Campos e indicadores útiles para el proyecto

### 5.1 Del API de calidad del aire

| Indicador propuesto | Fórmula / fuente | Uso |
|---|---|---|
| PM2.5 promedio anual por municipio | `avg(med_concentracion_estandar)` agrupado por año y municipio | Seguimiento de metas y comparación con normas |
| PM2.5 promedio mensual | `avg` por año-mes | Estacionalidad y alertas temporales |
| PM2.5 máximo diario y percentil 99 | Agregación horaria a diaria y `max`/percentil | Eventos extremos y protección de población sensible |
| Porcentaje de días > 15, > 25 y > 50 µg/m³ | Conteo de días-estación sobre umbrales | Indicador de exposición aguda |
| Número de estaciones activas y cobertura | `count(distinct estacion_id)` | Calidad del monitoreo |
| Tendencia anual (pendiente) | Regresión lineal o Theil-Sen sobre promedios anuales | Evaluación de avance hacia 2030 |
| Promedio móvil de 3 años | Media móvil de promedios anuales | Suavizar variabilidad interanual |
| Exposición ponderada por población | PM2.5 municipal × población municipal | Requiere población DANE (no está en el API) |

### 5.2 De los archivos de salud del proyecto

| Archivo | Campos clave | Indicadores que aporta |
|---|---|---|
| `AnalisisRiesgo_20082017.csv` | `municipio`, `grupo diagnóstico`, `nombre contaminante`, `sexo`, `edad`, `tipo de rezago`, `beta`, `exponencial del beta`, límites de confianza, `porcentaje del incremento del riesgo` | Coeficientes de riesgo atribuible a PM2.5, PM10 y O3 por municipio, grupo diagnóstico, sexo y edad |
| `EnfermedadesCalculadas_2008-2017.csv` | `Municipio`, `Periodo`, `Sexo`, `Edad`, `Grupo`, `Capitulo`, `casos` | Casos de enfermedades respiratorias y cardiovasculares |
| `DefunsionesCalculadas_2008-2017.csv` | `Municipio`, `Periodo`, `Sexo`, `Edad`, `Capitulo`, `Grupo`, `Muertes` | Defunciones por causa y grupo de edad |
| `TasaMortalidad_2008-2017.csv` | `Año`, `Municipio`, `Capítulo`, `Sexo`, `TasaMortalidadAjustada` | Tasas ajustadas de mortalidad respiratoria y circulatoria |

### 5.3 Llaves de integración API ↔ salud

| API | Salud | Tipo de cruce | Nota |
|---|---|---|---|
| `municipio` | `municipio_normalizado` | Texto normalizado (tildes, mayúsculas) | Unificar `Itagui/Itagüí`, `Medellin/Medellín` |
| `med_fecha_inicio` → año | `Periodo` | Año | Agregar API a escala anual |
| `msfl_code = 'PM2.5'` | `nombre contaminante = 'pm25'` | Dimensión contaminante | Estandarizar el código |
| `codigo_municipio` | Código DANE (si se añade) | Numérico | Recomendado para joins robustos |
| `estacion_id`, latitud, longitud | Municipio | Espacial | Permite asignar estaciones a municipios |

**Limitación central:** los CSV originales de salud cubren **2008–2017** y el aire **2020–2025**, sin años en común. Sin embargo, las fuentes complementarias verificadas (sección 8) permiten un solapamiento parcial: morbilidad 2019–2023 con aire 2020–2023, y mortalidad 2024–2025 con aire 2024–2025. Por lo tanto:

- Con los CSV originales no es posible una correlación directa; con las fuentes complementarias se puede explorar una **asociación ecológica 2020–2023**, con cautela y sin inferencia causal.
- La estrategia principal sigue siendo usar los **coeficientes beta** de `AnalisisRiesgo` como función de transferencia y aplicarlos a la exposición actual (como ya hace el proyecto con SIATA).
- Para correlación y modelos predictivos, cargar morbilidad 2019–2023 y mortalidad 2024–2025, y **armonizar estaciones** antes de empalmar 2015–2019 con 2020–2025.

---

## 6. Indicadores de salud relacionados con PM2.5

### 6.1 Coeficientes de riesgo de `AnalisisRiesgo` para PM2.5

El archivo contiene **392 modelos para PM2.5** (de 1.652 registros totales). Los coeficientes beta van de **0,00002 a 0,2318** (mediana 0,0737) y el porcentaje de incremento del riesgo de **0,01% a 26,1%** (mediana 7,66%).

| Grupo diagnóstico | Modelos | % incremento del riesgo (mín–máx) | Edad más vulnerable |
|---|---:|---:|---|
| Otras infecciones agudas de las vías respiratorias inferiores (J20–J22) | 68 | 2,29–26,10 | Menores de 5 años |
| Enfermedades del sistema respiratorio (J00–J99) | 116 | 1,72–20,89 | Menores de 5 años |
| Infecciones agudas de las vías respiratorias superiores (J00–J06) | 113 | 0,86–17,99 | Menores de 5 años |
| Influenza [gripe] y neumonía (J09–J18) | 57 | 0,01–16,69 | Menores de 5 años |
| Enfermedades del oído medio y de la mastoides (H65–H75) | 38 | 1,39–11,55 | Menores de 5 años |

**Modelos con mayor riesgo (PM2.5):**

| Municipio | Grupo diagnóstico | Sexo | Edad | Rezago | % incremento | Beta |
|---|---|---|---|---|---:|---:|
| Medellín | J20–J22 | Mujer | Menores de 5 años | Distribuido | 26,10 | 0,2318 |
| Medellín | J20–J22 | Ambos sexos | Menores de 5 años | Distribuido | 25,26 | 0,2252 |
| Medellín | J20–J22 | Hombre | Menores de 5 años | Distribuido | 24,40 | 0,2183 |
| La Estrella | J00–J99 | Ambos sexos | Menores de 5 años | Distribuido | 20,89 | 0,1896 |
| Medellín | J20–J22 | Mujer | Menores de 5 años | Distribuido | 20,49 | 0,1864 |

> **Precaución metodológica:** el porcentaje de incremento corresponde a `exp(beta) − 1`. Para interpretarlo como “por cada X µg/m³” es necesario conocer el incremento de exposición usado en el modelo. La literatura y la estructura de los valores sugieren un incremento de referencia de **10 µg/m³**; sin embargo, el proyecto debe confirmarlo con la fuente original del AMVA/ONS. Si se asume erróneamente que beta es “por 1 µg/m³”, los riesgos se sobrestiman de forma severa.

### 6.2 Tendencia histórica de salud (2008–2017)

| Año | Casos respiratorios | Tasa de mortalidad respiratoria ajustada (media) |
|---|---:|---:|
| 2008 | 47.193 | 57,4 |
| 2009 | 44.711 | 54,9 |
| 2010 | 83.066 | 59,6 |
| 2011 | 106.179 | 51,2 |
| 2012 | 123.643 | 53,4 |
| 2013 | 142.188 | 61,4 |
| 2014 | 146.462 | 55,0 |
| 2015 | 167.919 | 61,5 |
| 2016 | 145.968 | 69,9 |
| 2017 | 164.526 | 70,7 |

**Lectura:** los casos respiratorios pasaron de 47.193 (2008) a 164.526 (2017), un aumento nominal de **+249%**. La tasa ajustada de mortalidad respiratoria subió de 57,4 a 70,7 por 100.000 (**+23%**). Estos aumentos deben interpretarse con cautela: pueden reflejar mejoras en el reporte, cambios en la cobertura del sistema de salud y dinámica poblacional, no solo cambios en la contaminación. En 2017, el **95,3% de los casos registrados** corresponden a causas respiratorias (el archivo incluye solo grupos respiratorios y dos cardiovasculares).

**Nota de comparabilidad:** esta serie 2008–2017 proviene de los CSV del proyecto (casos/registros) y no es directamente comparable con las consultas externas 2019–2023 de DSSA ni con las muertes por IRA 2024–2025. No empalmar las tres fuentes sin armonizar definiciones, denominadores y cobertura.

### 6.3 Estrategia de integración salud–aire

1. **Transferencia de riesgo:** aplicar `riesgo_relativo = exp(beta × ΔPM2.5 / 10)` con beta del municipio, grupo diagnóstico, sexo y edad.
2. **Riesgo atribuible:** `fracción_atribuible = (RR − 1) / RR` para estimar la proporción de casos asociada a la exposición.
3. **Casos evitados:** `casos_evitados = casos_base × (1 − exp(−beta × ΔPM2.5 / 10))`.
4. **Rezago:** usar `tipo de rezago` (Simple/Distribuido) para modelar el efecto diferido; el proyecto ya contempla alertas de riesgo diferido (LAG).
5. **Validación:** con la morbilidad 2019–2023 y la mortalidad 2024–2025 ya verificadas (sección 8), comparar las estimaciones del modelo con los casos observados y calibrar. Para 2024–2025 usar el consolidado completo, no el archivo preliminar de DSSA.

---

## 7. ¿Se llegará a la meta de reducir las emisiones un 49% en 2030?

### 7.1 Contexto de la meta

El **PIGECA 2017–2030** (Acuerdo Metropolitano 16 de 2017) establece:

- **Meta de emisiones:** llegar a **915 t/año de PM2.5** en 2030. Frente a la línea base 2015 (~1.795 t/año), esto equivale a una reducción de **~49%**.
- **Meta de concentración anual de PM2.5:** **23 µg/m³** en 2030.
- **Meta de concentración de 24 h:** **15 µg/m³** en 2030.
- **Norma colombiana (Resolución 2254 de 2017):** 25 µg/m³ anual y 50 µg/m³ en 24 h.
- **Guía OMS 2021:** 5 µg/m³ anual y 15 µg/m³ en 24 h.

### 7.2 Escenarios con los datos disponibles

| Escenario | PM2.5 anual (µg/m³) | Comentario |
|---|---:|---|
| Línea base PIGECA 2015 | 33,0 | Valor de referencia del plan |
| Observado 2025 (corregido) | 14,8 | Promedio de medias anuales por estación |
| Meta PIGECA 2030 | 23,0 | Meta anual de concentración |
| −49% frente a 2015 | 16,8 | 33,0 × 0,51 |
| Proyección lineal 2020–2025 | ~16,0 | Pendiente prácticamente plana; alta incertidumbre |
| −49% frente a 2025 | 7,5 | 14,8 × 0,51; exigiría −12,6% anual |
| Guía OMS 2021 | 5,0 | Referencia de salud pública |

**Interpretación:**

- **En concentración, el nivel de 2025 (14,8 µg/m³) está por debajo del equivalente de una reducción del 49% frente a 2015 (16,8 µg/m³) y de la meta PIGECA 2030 (23 µg/m³).** Sin embargo, la línea base 2015 (33,0 µg/m³) no es directamente comparable con la serie 2020–2025: el dato IDEAM de 2015 tiene solo 6 estaciones y sobrerrepresenta tráfico. La comparación es indicativa, no concluyente.
- **Pero la tendencia 2020–2025 es plana**, no descendente. No hay evidencia en estos datos de que se esté avanzando hacia una reducción adicional del 49% frente al nivel actual (7,5 µg/m³). Para lograrlo se requeriría una reducción de **~12,6% anual**, muy superior a la variación observada (~−2,8% anual entre 2020 y 2025, y pendiente lineal prácticamente nula por el pico de 2024).
- **La meta de 24 h no se cumple:** la mediana diaria regional es 15,2 µg/m³ y 51,6% de los días-estación superan 15 µg/m³. La meta PIGECA de 15 µg/m³ en 24 h para 2030 es, por tanto, el indicador más exigente.
- **El dataset no mide emisiones.** Para verificar el −49% de emisiones se necesita el inventario oficial del AMVA/UPB (toneladas/año por sector y categoría vehicular), no concentraciones. La API no cubre 2015–2019, pero IDEAM sí publica PM2.5 anual por estación 2007–2024 (sección 8); aun así, 2015–2017 tienen 6–10 estaciones y 2019 solo 2, por lo que no se puede reconstruir una línea base regional homogénea sin armonizar estaciones.
- **Conclusión prudente:** con la información disponible, la meta de concentración anual parece cumplida o muy cerca, pero la comparación con 2015 no es homogénea; la meta de emisiones no es verificable con esta API y la evidencia 2018 (secundaria) sugiere que las emisiones pudieron aumentar; la meta de 24 h y la reducción adicional frente a 2025 no están soportadas por la tendencia observada. Se requiere el inventario primario y una serie 2015–2019 armonizada para una conclusión definitiva.

### 7.3 Beneficio potencial en salud de una reducción del 49%

Usando los coeficientes beta de PM2.5 y los casos respiratorios de 2017 (164.526) como base, se estiman los casos evitados por año:

| Escenario de reducción | ΔPM2.5 | Beta mediana (0,0737) | Beta máxima (0,2318) |
|---|---:|---:|---:|
| −49% frente a 2015 (33 → 16,8) | 16,2 µg/m³ | 11,3% de reducción; ~18.500 casos evitados | 31,3%; ~51.500 casos evitados |
| −49% frente a 2025 (14,8 → 7,5) | 7,25 µg/m³ | 5,2%; ~8.600 casos evitados | 15,5%; ~25.500 casos evitados |

**Lectura:** el beneficio en salud puede ser sustancial, especialmente en menores de 5 años y en enfermedades respiratorias agudas. Sin embargo, estas cifras son **estimaciones de escenario**, no proyecciones validadas: dependen del supuesto de escala de beta, de usar casos de 2017 como base, de no considerar crecimiento/ envejecimiento poblacional y de asumir una relación lineal y estable en el tiempo.

---

## 8. Fuentes complementarias verificadas para cerrar brechas

La API `g4t8-zkc3` cubre 2020–2025 y no contiene salud, población ni emisiones. El 2026-11-02 se verificaron fuentes oficiales en línea para cerrar total o parcialmente esas brechas. La tabla siguiente resume qué existe, qué se pudo descargar y qué límites tiene.

### 8.1 Inventario de fuentes

| Brecha | Fuente oficial | Cobertura verificada | Acceso | Uso recomendado | Limitación principal |
|---|---|---|---|---|---|
| PM2.5 anual por estación | IDEAM, `D_Concentracion_PM2.5.xlsx` | 2007–2024; 200 filas de estaciones; 37 del AMVA; 26 con dato en 2024 | Descarga directa XLSX | Serie histórica por estación y contraste con la API | No trae municipio; la mezcla de estaciones cambia; 2019 solo tiene 2 estaciones del AMVA |
| Excedencias de PM2.5 | IDEAM, `D_Excedencias_PM2.5.xlsx` | 2007–2024; porcentaje de excedencias a la norma de 24 h | Descarga directa XLSX | Contexto histórico de cumplimiento | Misma limitación de mezcla de estaciones que la concentración anual |
| PM2.5 diario/horario histórico | SISAIRE, consultas | Por estación, municipio, año, día u hora | Formulario web | Rellenar 2015–2019 y 2025 a escala diaria/horaria | No es descarga masiva; requiere interacción o scraping |
| Población municipal | DANE, proyecciones PPED | 2018–2042; total, cabecera y rural; sexo y edad | Descarga directa XLSX | Denominadores para tasas por 100.000 | Proyecciones, no conteos censales; actualización post-COVID |
| Morbilidad municipal | Secretaría Seccional de Salud de Antioquia, “Estadísticas de morbilidad” | 2019–2024; 10 municipios; 22 grandes causas; columna 10 = enfermedades del sistema respiratorio | XLSX por año | Serie 2019–2023 de consultas externas respiratorias | El archivo 2024 está incompleto: 21.463.272 atenciones vs. 38.358.166 en 2023 |
| Mortalidad municipal | DANE, “Defunciones no fetales” | 2018–2025; 2024 y 2025 verificados (2024: 275.778 casos y 61 variables) | XLSX agregados y microdatos | Muertes por infecciones respiratorias agudas (causa 108) por municipio de residencia | La lista 6/67 solo separa infecciones respiratorias agudas; las crónicas requieren microdatos o la lista 105 |
| Emisiones 2015/2016 | EPM/AMVA, `Informe_Inventario_emisiones_2015.pdf` | Valle de Aburrá; móviles 2015 y fijas 2016; 10 municipios | PDF | Línea base y desagregación por sector/municipio | No es máquina-legible; móviles y fijas son de años distintos |
| Emisiones 2018 | AMVA/UPB, inventario 2018 (síntesis secundaria) | Valle de Aburrá; móviles y fijas 2018 | Resumen periodístico | Contexto de la evolución de emisiones | No se localizó el informe primario; las cifras no son directamente comparables |
| SIATA histórico | SIATA, repositorio y portal de descargas | Datos horarios/diarios de la red de calidad del aire; histórico sujeto a registro | Endpoints públicos de los últimos 6 meses; descarga histórica con registro | Validación cruzada y relleno de vacíos | Registro para histórico; flags de calidad; la versión MVP no debe citarse en publicaciones |

### 8.2 Qué se puede afirmar ahora

#### PM2.5 histórico (2015–2019)

El archivo de IDEAM permite reconstruir promedios anuales por estación, pero **no una serie regional homogénea**. Para las estaciones marcadas como `AMVA`, los promedios no ponderados y el número de estaciones con dato son:

| Año | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Media AMVA (µg/m³) | 31,8 | 32,9 | 26,2 | 19,9 | 22,6 | 19,1 | 16,9 | 17,6 | 16,9 | 18,1 |
| Estaciones con dato | 6 | 8 | 10 | 21 | 2 | 22 | 24 | 23 | 21 | 26 |

Lectura correcta:

- **2015–2017 no es una línea base regional comparable:** solo hay 6–10 estaciones y están sobrerrepresentadas estaciones de alto tráfico y de fondo urbano con niveles altos (Casa Justicia, Tráfico Centro, Tráfico Sur, U. Nal.), que elevan el promedio.
- **2018 es el año histórico más comparable** con la serie 2020–2024: 21 estaciones y media de 19,9 µg/m³.
- **2019 no sirve como promedio regional:** solo 2 estaciones del AMVA tienen dato (22,6 µg/m³).
- **2024 valida parcialmente la corrección de la API:** IDEAM reporta 18,1 µg/m³ (26 estaciones) y la API corregida 18,3 µg/m³. En 2020–2023 la diferencia es de 1,9–3,1 µg/m³ (IDEAM mayor), atribuible a la mezcla de estaciones y a la incertidumbre de la corrección de escala.
- **No se debe empalmar 2015–2019 con 2020–2025 sin armonizar estaciones.** Para una serie regional robusta hay que seleccionar un panel fijo de estaciones con datos en ambos períodos o modelar la mezcla.

#### Población y denominadores

DANE publica la serie municipal 2018–2042 actualizada en julio de 2025. Para los 10 municipios del Valle de Aburrá:

| Año | 2018 | 2024 | 2025 |
|---|---:|---:|---:|
| Población total | 3.870.058 | 4.167.258 | 4.194.012 |

El crecimiento 2018–2025 es **+8,4%**. Usar estas cifras como denominador cambia las tasas frente a usar la población de 2005–2017 del proyecto; no mezclar denominadores de distintas proyecciones.

#### Morbilidad respiratoria municipal (2019–2024)

La Secretaría Seccional de Salud de Antioquia publica consultas externas por 22 grandes causas y municipio. La columna 10 corresponde a **enfermedades del sistema respiratorio**. Para los 10 municipios:

| Año | Consultas respiratorias | Población | Tasa por 100.000 | Estado |
|---|---:|---:|---:|---|
| 2019 | 1.113.540 | 3.943.900 | 28.234 | Comparable |
| 2020 | 528.047 | 4.027.667 | 13.110 | Comparable; caída por COVID-19 |
| 2021 | 383.227 | 4.076.915 | 9.400 | Comparable; caída por COVID-19 |
| 2022 | 1.279.396 | 4.109.187 | 31.135 | Comparable; rebote |
| 2023 | 1.451.388 | 4.136.142 | 35.090 | Comparable; año más alto de la serie |
| 2024 | 661.703 | 4.167.258 | 15.879 | **Incompleto; no usar para tendencia** |

Advertencias:

- Son **consultas externas**, no casos únicos ni incidencia. Una persona puede generar varias consultas.
- La caída 2020–2021 y el rebote 2022–2023 están confundidos por el **uso de servicios de salud y la pandemia de COVID-19**, no solo por cambios en la enfermedad respiratoria.
- El archivo 2024 contiene 21.463.272 atenciones totales frente a 38.358.166 en 2023 (**−44%**), y la participación de Medellín sube a 82% (vs. 67–73% en 2019–2022). Es un archivo preliminar/incompleto generado el 21-07-2025; no debe usarse para concluir una caída real.

#### Mortalidad por infecciones respiratorias agudas (2024–2025)

DANE publica los cuadros unificados de defunciones no fetales por municipio de residencia. En la lista 6/67, la causa **108 “Infecciones respiratorias agudas”** permite un corte comparable y municipal. Para los 10 municipios:

| Año | Muertes por IRA (causa 108) | Población | Tasa por 100.000 |
|---|---:|---:|---:|
| 2024 | 1.132 | 4.167.258 | 27,2 |
| 2025 | 1.331 | 4.194.012 | 31,7 |

Las muertes absolutas por IRA aumentaron **+17,6%** entre 2024 y 2025. Esto **no implica** que el aumento sea atribuible a PM2.5: es un indicador de resultado para validación, no una prueba causal. Para enfermedades respiratorias crónicas (J40–J47) se necesita el microdato de DANE o la lista 105, que no está desagregada por municipio en el cuadro 6/67.

#### Emisiones

- **Inventario 2015/2016 (EPM/AMVA):** 1.496 t/año de PM2.5 por fuentes móviles (2015) + 334 t/año por fuentes fijas (2016) = **~1.830 t/año**. Es consistente con la línea base PIGECA de ~1.795 t/año.
- **Actualización 2018 (síntesis secundaria):** 2.625 t/año móviles + 248 t/año fijas = **~2.873 t/año**. Si se confirma con el informe primario, las emisiones habrían aumentado, sobre todo por transporte, y la meta de 915 t/año sería más exigente que lo sugerido por la línea base.
- **Meta PIGECA 2030:** 915 t/año, ~49% menos frente a ~1.795 t/año.
- **No usar el PDF `inventario-emisiones_2020_final.pdf` de rds.org.co para el AMVA:** ese documento corresponde a **Bogotá** (Secretaría Distrital de Ambiente), no al Valle de Aburrá. Es un error de atribución frecuente.
- **No se localizó una serie abierta, máquina-legible y comparable de emisiones por año para el AMVA.** Para verificar la meta hay que solicitar los inventarios primarios AMVA/UPB (2018 y 2022) y documentar metodología y año base.

#### SIATA

SIATA es la fuente más adecuada para validación horaria y para el componente de tiempo real del proyecto:

- Endpoints públicos de los últimos 6 meses: `https://siata.gov.co/EntregaData1/Datos_SIATA_Aire_pm25.json` (y análogos para PM10, NO2, O3, CO, SO2).
- Portal de descargas históricas con registro: `https://siata.gov.co:8018/descarga_siata/` y tutorial: `https://siata.gov.co/sitio_web/index.php/tutoriales`.
- Repositorio de archivos: `https://siata.gov.co/CalidadAire/` (carpetas `ReporteDiario/`, `ReporteHorario/`, `Gravimetria/`, `GestionAire/`).
- Metadatos y disponibilidad: `https://doi.org/10.83041/xti3fh`.

Usar SIATA para comparar la API/IDEAM en 2024–2025 y para llenar vacíos, pero **respetar los flags de calidad** (en la API histórica de SIATA, valores con flag > 2,5 no son buena calidad) y no citar la versión MVP en publicaciones.

### 8.3 Integración al pipeline

Tablas mínimas y llaves recomendadas:

| Tabla | Grano | Llaves | Campos mínimos |
|---|---|---|---|
| `poblacion_municipal` | municipio-año-área-sexo-edad | `codigo_dane`, `anio`, `area`, `sexo`, `edad` | `poblacion`, `fuente`, `es_proyeccion` |
| `pm25_anual_estacion` | estación-año | `codigo_estacion`, `anio` | `pm25_anual`, `n_horas_validas`, `fuente`, `mezcla_estaciones` |
| `morbilidad_municipal` | municipio-año-causa | `codigo_dane`, `anio`, `causa` | `atenciones`, `fuente`, `es_preliminar` |
| `defunciones_municipal` | municipio-año-causa | `codigo_dane`, `anio`, `causa` | `muertes`, `fuente`, `lista_causas` |
| `emisiones_anuales` | año-sector-contaminante | `anio`, `sector`, `contaminante` | `toneladas`, `metodologia`, `fuente`, `es_comparable` |

Reglas de integración:

1. **Unir por código DANE del municipio**, no por nombre. Normalizar tildes y variantes (`Itagüí`/`Itagui`, `Medellín`/`Distrito Especial…`).
2. **No unir por nombre de estación.** Usar `codigo_estacion` y una tabla de equivalencias SISAIRE/SIATA.
3. **Marcar la fuente y la comparabilidad** en cada fila: `fuente`, `metodologia`, `es_preliminar`, `es_comparable`, `anio_base`.
4. **Calcular tasas con denominadores DANE** del mismo año y área; reportar por 100.000 habitantes.
5. **Validar 2024 API vs. IDEAM** (18,3 vs. 18,1 µg/m³) y **API vs. SIATA** en las estaciones con dato horario.
6. **No mezclar** el inventario 2015/2016 con el 2018 ni con la meta 2030 sin una tabla de equivalencias metodológicas.

### 8.4 Advertencias y descartes

- **IDEAM no es una serie regional poblacional:** es un promedio de estaciones; la mezcla cambia y 2019 solo tiene 2 estaciones del AMVA.
- **El archivo de morbilidad 2024 está incompleto.** Usar 2019–2023 para tendencia y solicitar el consolidado 2024–2025 a la Secretaría de Salud de Antioquia o a SISPRO.
- **La mortalidad 2024–2025 solo permite IRA (causa 108).** Para crónicas, usar microdatos DANE y CIE-10 J40–J47.
- **Los inventarios de emisiones no son comparables entre años** sin verificar metodología, año base y cobertura de fuentes.
- **El dataset `yspz-pxxn` de datos.gov.co no sirve para este proyecto:** contiene 843 registros de Chinchiná (Caldas), no del Valle de Aburrá.
- **La escala de beta sigue sin confirmarse:** se asume un incremento de 10 µg/m³; verificar en la fuente original antes de reportar casos evitados.

### 8.5 URLs verificadas

```text
# IDEAM — promedios anuales y excedencias PM2.5
https://bart.ideam.gov.co/indiecosistemas/ind/aire/datos/D_Concentracion_PM2.5.xlsx
https://bart.ideam.gov.co/indiecosistemas/ind/aire/datos/D_Excedencias_PM2.5.xlsx

# IDEAM/SISAIRE — consultas históricas por estación/municipio
https://sisaire.ideam.gov.co/ideam-sisaire-web/consultas.xhtml

# DANE — proyecciones municipales 2018–2042
https://www.dane.gov.co/files/censo2018/proyecciones-de-poblacion/Municipal/PPED-AreaMun-2018-2042_VP.xlsx
https://www.dane.gov.co/files/censo2018/proyecciones-de-poblacion/Municipal/PPED-AreaSexoEdadMun-2018-2042_VP.xlsx

# DANE — defunciones no fetales 2024 y 2025 (cuadros unificados)
https://www.dane.gov.co/files/operaciones/EEVV/2026/6-feb-2026/anex-EEVV-DefuncionesNoFetalesCuadroUnificado-2024.xlsx
https://www.dane.gov.co/files/operaciones/EEVV/2026/24-sep-2026/anex-EEVV-DefuncionesNoFetalesCuadroUnificado-2025.xlsx

# DANE — microdatos EEVV 2024 (puede requerir registro)
https://microdatos.dane.gov.co/index.php/catalog/878

# Secretaría Seccional de Salud de Antioquia — morbilidad municipal
https://dssa.gov.co/estadisticas-de-morbilidad/
# Archivos anuales (base: https://dssa.gov.co/OSSSA/Archivos/Morbilidad/A%C3%B1os/)
https://dssa.gov.co/OSSSA/Archivos/Morbilidad/A%C3%B1os/2019/24.4.2ConsultaSegunAgrupacion22RegionyMpio2019.xlsx
https://dssa.gov.co/OSSSA/Archivos/Morbilidad/A%C3%B1os/2020/24.4.2ConsultaSegunAgrupacion22RegionyMpio2020.xlsx
https://dssa.gov.co/OSSSA/Archivos/Morbilidad/A%C3%B1os/2021/2ConsultaSegunAgrupacion22RegionyMpio2021.xlsx
https://dssa.gov.co/OSSSA/Archivos/Morbilidad/A%C3%B1os/2022/2CausasConsMorbilidadSubreMunicipio2022%2020102023.xlsx
https://dssa.gov.co/OSSSA/Archivos/Morbilidad/A%C3%B1os/2023/22GRANDESCONSULTAS2023.xlsx
https://dssa.gov.co/OSSSA/Archivos/Morbilidad/A%C3%B1os/2024/22GRANDESCONSULTAS2024.xlsx

# SISPRO — consulta de atenciones en salud
https://www.sispro.gov.co/central-gestion-del-conocimiento/Pages/Construya-su-consulta-afiliaciones-en-salud.aspx

# AMVA/EPM — inventario de emisiones 2015
https://www.epm.com.co/content/dam/epm/clientes-y-usuarios/gas/constructor-y-urbanizador/gas-natural-vehicular/gas-natural-vehicular2/Informe_Inventario_emisiones_2015.pdf

# SIATA — datos y repositorio
https://siata.gov.co/EntregaData1/Datos_SIATA_Aire_pm25.json
https://siata.gov.co:8018/descarga_siata/
https://siata.gov.co/CalidadAire/
https://doi.org/10.83041/xti3fh
```

---

## 9. Limitaciones

1. **Salud y aire se solapan solo parcialmente.** El proyecto original cubre salud 2008–2017; las fuentes oficiales verificadas permiten extender morbilidad a 2019–2023 y mortalidad a 2024–2025, con solapamiento 2020–2023 y 2024–2025 según el indicador. Aun así, no hay una serie única y homogénea 2015–2025 para todos los indicadores.
2. **Error de escala 2020–2023** en varias estaciones del AMVA. La corrección aplicada es un diagnóstico, no una validación oficial.
3. **El API no contiene emisiones, población ni datos de salud.** Solo concentraciones y meteorología; las brechas se cubren parcialmente con las fuentes de la sección 8.
4. **Cobertura de estaciones limitada y desigual:** 30–32 estaciones para 10 municipios; no hay representación poblacional uniforme.
5. **Frecuencia horaria, no diaria:** las excedencias diarias requieren agregación con criterio de completitud (≥18 h).
6. **Posible rezago en la publicación:** el dataset consultado termina el 2025-12-31, aunque la consulta se hizo en 2026.
7. **Escala de beta ambigua:** se asume un incremento de referencia de 10 µg/m³; debe confirmarse con la fuente original.
8. **Estaciones indicativas vs fijas:** las indicativas pueden tener menor calidad; para series oficiales, priorizar `tipo_estacion = 'Fija'` y `nombre_fgda = 'AMVA'`.
9. **No se verificaron duplicados** a nivel de estación-hora-contaminante; se recomienda una validación en la base de datos.
10. **La serie IDEAM 2015–2019 no es homogénea:** 2015–2017 tienen 6–10 estaciones y 2019 solo 2; no se puede empalmar con 2020–2025 sin armonizar la mezcla de estaciones.
11. **El archivo DSSA 2024 está incompleto:** 21.463.272 atenciones vs. 38.358.166 en 2023; no usar para tendencia.
12. **La mortalidad 2024–2025 solo permite IRA (causa 108):** las enfermedades respiratorias crónicas requieren microdatos DANE o la lista 105.
13. **Los inventarios de emisiones no son comparables entre años:** 2015/2016, 2018 y 2030 usan metodologías y coberturas distintas; el PDF 2020 de rds.org.co es de Bogotá, no del AMVA.

---

## 10. Recomendaciones

1. **Cargar este API como fuente histórica de aire** en el pipeline, en una tabla `mediciones_aire_historico` con llaves: `estacion_id`, `municipio`, `contaminante`, `fecha_hora`, `concentracion`, `unidad`, `duracion_min`, `tipo_estacion`, `fuente`.
2. **Agregar una bandera de calidad** (`escala_sospechosa`, `valor_atipico`, `horas_validas_dia`) y documentar la corrección 2020–2023.
3. **Construir indicadores anuales y mensuales** por municipio y estación, con promedios móviles de 3 años y pendientes.
4. **Calcular excedencias diarias** (15, 25 y 50 µg/m³) con el criterio de ≥18 h válidas.
5. **Cruzar con `AnalisisRiesgo`** usando beta por municipio, grupo diagnóstico, sexo y edad; reportar riesgo atribuible y casos evitados.
6. **Cargar la morbilidad municipal 2019–2023 y la mortalidad 2024–2025 ya verificadas**; solicitar a la Secretaría de Salud de Antioquia/SISPRO el consolidado 2024–2025 y a DANE los microdatos para enfermedades crónicas.
7. **Descargar IDEAM 2007–2024 y solicitar al AMVA/UPB los inventarios primarios 2018/2022**, además de una serie 2015–2019 armonizada, para evaluar el −49% con rigor.
8. **Comparar con SIATA** (tiempo real) para calibrar y detectar sesgos entre fuentes.
9. **Priorizar la meta de 24 h** (15 µg/m³) y la protección de menores de 5 años, que concentran los mayores coeficientes de riesgo.
10. **Usar denominadores DANE 2018–2042** y recalcular tasas por 100.000; no mezclar con la población 2005–2017 del proyecto.
11. **No usar el archivo DSSA 2024 para tendencia** hasta que esté completo; marcarlo como preliminar.
12. **Validar la API contra IDEAM 2024 (18,3 vs. 18,1 µg/m³) y SIATA**, reportando diferencias por estación.
13. **Documentar fuente, metodología y comparabilidad** en cada tabla; usar flags `es_preliminar`, `es_comparable`, `anio_base`.

---

## 11. Reproducibilidad

- **Endpoint:** `https://www.datos.gov.co/resource/g4t8-zkc3.json`
- **Consulta de metadatos:** `https://www.datos.gov.co/api/views/g4t8-zkc3.json`
- **Filtro base para el Valle de Aburrá:**

```text
msfl_code='PM2.5'
AND departamento='Antioquia'
AND municipio in('Medellín','Bello','Itagüí','Envigado','Sabaneta','Caldas','La Estrella','Copacabana','Girardota','Barbosa')
```

- **Período analizado:** `med_fecha_inicio >= '2020-01-01' AND med_fecha_inicio < '2026-01-01'`
- **Agregación anual:** `substring(med_fecha_inicio,1,4)`
- **Agregación mensual:** `substring(med_fecha_inicio,1,7)`
- **Agregación diaria:** `substring(med_fecha_inicio,1,10)` + filtro `duraci_n=60` + mínimo 18 horas por día.
- **Corrección de escala:** comparar cada estación-año contra su referencia 2024–2025 y dividir por 1, 10 o 100 según el ratio.

### Fuentes complementarias

Las URLs verificadas, hojas y filtros están en la sección 8.5. Las cifras de morbilidad y mortalidad se calcularon con `pandas`, `openpyxl` y `pypdf` a partir de los archivos descargados el 2026-11-02. Para reproducir:

1. Descargar los XLSX de IDEAM y DANE, y los XLSX anuales de DSSA.
2. Filtrar los 10 municipios por código DANE (`05001`, `05088`, `05129`, `05212`, `05266`, `05308`, `05360`, `05364`, `05631`, `05686`).
3. En DSSA, usar la columna 10 (`Enfermedades del sistema respiratorio`) y no la columna 22 (`Códigos para propósitos especiales`).
4. En DANE, usar `Cuadro5` (municipio en columna 3, causa en columna 4, conteo en columna 5) y la causa `108` para IRA.
5. Recalcular tasas con la población DANE del mismo año y marcar 2024 como preliminar.

### Consultas de verificación rápida

```bash
# Cobertura temporal de PM2.5
curl -s "https://www.datos.gov.co/resource/g4t8-zkc3.json?\$select=min(med_fecha_inicio),max(med_fecha_inicio)&\$where=msfl_code='PM2.5'"

# Conteo por contaminante
curl -s "https://www.datos.gov.co/resource/g4t8-zkc3.json?\$select=msfl_code,count(*)&\$group=msfl_code&\$order=count(*) desc"

# Municipios del Valle de Aburrá con PM2.5
curl -s "https://www.datos.gov.co/resource/g4t8-zkc3.json?\$select=municipio,count(*)&\$where=msfl_code='PM2.5' AND departamento='Antioquia'&\$group=municipio&\$order=count(*) desc"
```

---

## 12. Conclusión

El dataset `g4t8-zkc3` es una fuente **valiosa y utilizable** para el componente ambiental del proyecto: permite construir series históricas de PM2.5 (2020–2025) para los 10 municipios del Valle de Aburrá, con cobertura horaria y estaciones georreferenciadas. Su principal problema es el **cambio de escala 2020–2023**, que debe corregirse o marcarse antes de cualquier análisis. La serie corregida muestra niveles anuales de **~15–18 µg/m³**, por debajo de la norma colombiana y de la meta PIGECA anual, pero **por encima de la guía OMS** y con **excedencias diarias frecuentes**.

La verificación de fuentes complementarias (sección 8) cambia el diagnóstico de brechas. La brecha de aire 2015–2019 se cubre parcialmente con IDEAM (2007–2024), pero **no es una serie regional homogénea**: 2015–2017 tienen 6–10 estaciones y 2019 solo 2. La salud ya cuenta con morbilidad municipal 2019–2023 y mortalidad por IRA 2024–2025, lo que da **solapamiento 2020–2023** con el aire para morbilidad y **2024–2025** para mortalidad; la población DANE 2018–2042 permite recalcular tasas; y las emisiones tienen inventario 2015/2016 (~1.830 t/año) y una actualización 2018 secundaria (~2.873 t/año), pero no una serie abierta comparable. El archivo DSSA 2024 está incompleto y el PDF 2020 de rds.org.co es de Bogotá, no del AMVA.

Sobre la meta del **−49% al 2030**, la conclusión es matizada: en concentración anual el nivel de 2025 (14,8 µg/m³) está por debajo del equivalente de −49% frente a 2015 (16,8 µg/m³), pero **la línea base 2015 no es homogénea** y la comparación es indicativa; **no hay evidencia de una tendencia que sostenga una reducción adicional del 49% frente a 2025**; y la meta de emisiones **no es verificable con este API**, mientras la evidencia 2018 (secundaria) sugiere que las emisiones pudieron aumentar. La meta anual de concentración es plausible, la de 24 h no se cumple y la de emisiones queda pendiente de los inventarios primarios AMVA/UPB. Se recomienda usar las fuentes de la sección 8, solicitar los consolidados 2024–2025 y no empalmar series sin armonizar estaciones ni metodologías.
