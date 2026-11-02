¿Por qué usar datos 2008-2017 si no son actuales?
Argumento académico-técnico:
1. Son la fuente oficial más reciente disponible. Los CSVs provienen del Observatorio Nacional de Salud — la última publicación complete con microdatos abiertos de morbilidad y mortalidad del Valle de Aburrá. No existe un dataset público más reciente con ese nivel de desagregación (municipio × sexo × grupo_edad × diagnóstico CIE-10).
2. Los coeficientes β no cambian año a año. El analisis_riesgo contiene modelos de regresión que calculan la relación entre contaminación y enfermedad. Esa relación biológica (ej. "por cada µg/m³ de PM2.5, el riesgo de asma aumenta X%") es estructural, no coyuntural. Es válido aplicarla a mediciones actuales.
3. Es el enfoque estándar en epidemiología ambiental. Estudios reales usan coeficientes históricos para estimar riesgo actual. La OMS misma publica "funciones exposición-respuesta" que se usan durante años sin cambios.
¿El cálculo de riesgo es aproximado a la realidad?
Sí, y se justifica así:
Riesgo estimado = PM2.5_en_vivo × β_histórico
Componente	Fuente	Validez
PM2.5 en vivo	SIATA — red oficial del Área Metropolitana	Dato real, actual, minuto a minuto
β (coeficiente)	Modelo de regresión sobre 10 años de datos	Intervalo de confianza del 95% incluido en la BD (limite_inferior, limite_superior)
- El β tiene sus límites de confianza almacenados. El dashboard puede mostrar: "Riesgo estimado: 1.9% (IC 95%: 1.2% - 2.5%)" — eso le da rigurosidad estadística.
- Se calcula por municipio, no es un promedio regional genérico. Medellín (β=0.086) es más sensible que Envigado (β=0.072) → eso es biológicamente coherente.
Cómo decirlo en la sustentación
"Los datos de salud son de 2008-2017 porque es el período con microdatos abiertos más reciente del Observatorio Nacional de Salud. Pero los coeficientes β representan relaciones biológicas entre contaminación y enfermedad que son estables en el tiempo. Al multiplicarlos por el PM2.5 actual de SIATA, obtenemos una estimación de riesgo válida y útil para la toma de decisiones hoy."
"Además, la BD almacena los intervalos de confianza del β, permitiendo mostrar no solo el valor puntual sino su rango de incertidumbre, lo que le da transparencia estadística al cálculo."




Con datos en vivo de la BD, así se relaciona cada sección del dashboard:
Sección A: Estado Actual y Mapa de Calor
Mapa Leaflet.js → mediciones_siata (latitud, longitud, pm25_ica, categoria_ica)
Estación #12 - Tráfico Centro   | PM2.5=24.0 | (6.2526, -75.5696) ← pin rojo/moderado
Estación #94 - Santa Elena      | PM2.5=4.0  | (6.2364, -75.4985) ← pin verde/bueno
Cada pin se pinta según categoria_ica (Buena/Aceptable/Dañina a la salud de grupos sensibles/Dañina/Muy dañina/Peligrosa). Las coordenadas latitud/longitud vienen directo de la API de SIATA.
KPIs Promedio Regional → mediciones_siata con agregaciones:
PM2.5 promedio: 14.0  (AVG)
Estación más crítica: Estación #12 - Tráfico Centro con 24.0  (MAX)
Sección B: Calculadora de Riesgo (el diferenciador)
Cruza 3 tablas en una sola operación:
mediciones_siata.pm25_ica  ×  analisis_riesgo.beta  =  Riesgo estimado
      (en vivo)                    (histórico)
Flujo completo:
1. Usuario selecciona municipio + edad + sexo
2. El LIKE encuentra la estación: estacion ILIKE '%Medellín%' → PM2.5 actual
3. Se cruza con analisis_riesgo filtrando por municipio_id + contaminante_id (pm25) + grupo_edad + sexo
4. Cálculo: PM2.5_vivo × β = incremento_riesgo
Ejemplo real Medellín:
PM2.5=22.0 (Tráfico Centro)  ×  β=0.086302  =  1.90% de riesgo estimado
La tabla analisis_riesgo tiene β (coeficiente) y porcentaje_incremento_riesgo por municipio, contaminante, grupo_edad y sexo — eso permite filtrar por perfil demográfico.
Sección C: Tendencias Históricas
Gráfico de líneas → enfermedades vs defunciones por año:
Año	Casos (enfermedades)
2008	49,828
2017	172,707
Se agrupa por periodo y se suman casos/muertes. Se puede filtrar por municipio_id para ver la curva de un municipio específico.
Ranking de Morbilidad → enfermedades JOIN municipios:
Medellín     | 912,224 casos
Bello        |  79,576 casos
Itagüí       |  62,895 casos
...
La Estrella  |  14,068 casos
Resumen del flujo de datos por sección
Sección	Tablas involucradas
A - Mapa	mediciones_siata
A - KPIs	mediciones_siata
B - Riesgo	mediciones_siata + analisis_riesgo + municipios + contaminantes
C - Líneas	enfermedades + defunciones
C - Ranking	enfermedades + municipios
