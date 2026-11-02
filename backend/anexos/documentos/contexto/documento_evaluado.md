PIPELINE DE ADQUISICIÓN E INTEGRACIÓN DE DATOS AMBIENTALES: HACIA UN ÍNDICE DE EFECTOS DE LA CALIDAD DEL AIRE EN LA SALUD PÚBLICA DEL VALLE DE ABURRÁ 

 

Environmental data acquisition and integration pipeline: towards an index of the effects of air quality on public health in the Aburrá Valley 

 

Sub-eje temático 

 

Software, datos e inteligencia artificial. 

 

Palabras clave 

 

Adquisición de datos, Calidad del Aire; Enfermedades Respiratorias; Integración de Datos. 

 

Introducción 

 

La contaminación atmosférica por material particulado fino (PM2.5) representa un riesgo crítico para la salud pública, ya que sus diminutas partículas penetran profundamente en el sistema respiratorio y alcanzan el torrente sanguíneo, lo que incrementa la morbilidad y la mortalidad por enfermedades respiratorias y cardiovasculares [1], [2]. Ante esta amenaza, se han desarrollado soluciones tecnológicas para monitorear la calidad del aire, que combinan datos de estaciones oficiales de alta precisión, sensores de bajo costo, teledetección satelital y modelos de asimilación de datos para capturar la variabilidad de los contaminantes [3], [4]. 

La literatura científica ofrece estudios y metodologías para cuantificar los riesgos sanitarios y mejorar la gestión de los datos ambientales. La Organización Mundial de la Salud (OMS) desarrolló AirQ+ para estimar la carga de enfermedad atribuible a la contaminación mediante series temporales y tablas de vida [5]. Por su parte, Ferrer et al. [6] diseñaron un framework basado en redes de sensores de calidad del aire que incluye un flujo de datos (pipeline) con etapas de preprocesamiento, detección de anomalías e imputación estadística. Sserujongi et al. [7], señalan que diseñar un pipeline de adquisición e integración ambiental requiere conectar fuentes heterogéneas, aplicar preprocesamiento riguroso y fusionar variables para estimar índices de impacto en la salud. 

En Colombia, Piñeros-Jiménez et al. [8], identificaron que en Medellín el crecimiento poblacional, la urbanización acelerada y las condiciones geográficas han agravado la contaminación del aire, afectando la calidad de vida de sus habitantes. Por otra parte, el Proyecto PROMESA analizó el impacto de la contaminación del aire y del clima en la infancia desde la gestación y su influencia en el desarrollo de enfermedades en 506 niños de Bogotá y Medellín entre 2018y 2023 [9], mientras que Parra-Sánchez et al. [1] aplicaron analítica de datos bajo la metodología CRISP-DM para evidenciar la correlación entre los picos de PM2.5 y el aumento de las consultas hospitalarias en Medellín. 

El Área Metropolitana del Valle de Aburrá (AMVA) cuenta con sistemas de monitoreo ambiental, como el Sistema de Alerta Temprana del Valle de Aburrá (SIATA) [10] , y redes ciudadanas de sensores, como PurpleAir [11]. Sin embargo, persisten dificultades para evaluar los efectos del PM2.5 sobre la salud pública debido a la fragmentación de los datos ambientales y epidemiológicos. Además, métricas tradicionales como el Índice de Calidad del Aire (ICA) proporcionan valores generales que no reflejan directamente el riesgo epidemiológico según la vulnerabilidad demográfica [1]. 

Ante este escenario, se plantea el objetivo de diseñar e implementar un pipeline de adquisición e integración de datos basado en la Extracción, Transformación y Carga (ETL, por su sigla en inglés) en Python que fusione en tiempo real las mediciones de PM2.5 del SIATA con conjuntos de datos epidemiológicos. 

 

Metodología 

 

Este trabajo se enmarca en una investigación aplicada de carácter tecnológico, con un enfoque metodológico exploratorio, cuantitativo y descriptivo-experimental, orientado al diseño y la validación de un pipeline para la adquisición e integración de datos ambientales y epidemiológicos. Las variables ambientales incluyeron PM2.5, la velocidad del viento y el ICA. Las variables epidemiológicas incluyeron tasas de mortalidad, defunciones y coeficientes de riesgo (β), desagregados por sexo y edad. Los instrumentos de medición fueron las estaciones oficiales de SIATA y los registros epidemiológicos del AMVA. El proceso metodológico comprendió tres fases: 1) Identificación de fuentes, 2) exploración y transformación de datos y 3) integración y carga de datos. 

Fase 1. Identificación de fuentes de datos 

 

El estudio identificó fuentes de datos heterogéneas clasificadas en dos dimensiones: 

 

Ambiental. Mediciones en tiempo real obtenidas de la API del SIATA, que incluyen la concentración de material particulado fino (PM2.5) en µg/m³, la velocidad del viento, las coordenadas geográficas de las estaciones y el ICA [10]. 

Epidemiológica. Cuatro conjuntos de datos históricos en formato CSV (Análisis de Riesgo, Enfermedades Calculadas, Tasas de Mortalidad y Defunciones) provenientes del portal de datos abiertos del Área Metropolitana, correspondientes al período 2008–2017. Estos registros contienen coeficientes epidemiológicos (beta, β), porcentajes de incremento del riesgo, casos y fallecimientos, desagregados por municipio, sexo, rangos etarios (menores de 5 años, de 5 a 14 años y mayores de 65 años) y diagnósticos según la codificación CIE-10. 

Fase 1. Exploración y transformación de datos 

 

El pipeline siguió el procedimiento ETL [12] y se desarrolló en Python, utilizando las librerías Requests (extracción vía HTTP), Pandas (procesamiento tabular), Psycopg2 (conexión a PostgreSQL) y Schedule (automatización de tareas). Los datos se almacenaron en un motor relacional PostgreSQL en la nube, estructurado bajo un modelo de tablas de dimensión y hecho. 

Extracción. Se realizaron peticiones HTTP GET la API del SIATA cada dos minutos para capturar actualizaciones continuas de los sensores, complementadas con la ingesta de archivos epidemiológicos históricos (Fig. 2). 

Transformación. Se realizó la conversión de los códigos de error por mantenimiento de sensores (-999) a valores nulos (NULL). Para evitar distorsiones estadísticas, se normalizaron los formatos numéricos, se estandarizaron los nombres de los municipios eliminando variantes ortográficas, se reemplazaron las comas por puntos para convertir cadenas de texto a tipo flotante (float) y se crearon columnas numéricas de indexación (_cod) para las variables demográficas. Se calculó, además, la amplitud del intervalo de confianza (ancho_ic) para evaluar la precisión estadística de las estimaciones de riesgo. 

Carga: Se realizó el almacenamiento en PostgreSQL y la creación de la vista consolidada vista_riesgo_integrado, que vincula en tiempo real las mediciones de PM2.5 con los coeficientes epidemiológicos históricos según municipio, sexo, edad y diagnóstico. La validación técnica se apoyó en el Análisis Exploratorio de Datos (EDA) en Python sobre los cinco datasets de origen para verificar tipos y distribuciones, con pruebas de 

persistencia e inserción continua mediante scripts automatizados cada dos minutos, y con la verificación funcional de las respuestas servidas por los endpoints de la API frente a escenarios de consulta parametrizada. 

 

Resultado preliminares 

 

La ejecución del pipeline de datos permitió contar con un conjunto de datos (dataset) integrado que incluye información ambiental en tiempo real y registros epidemiológicos históricos. Se logró la ingesta y estructuración de 1,652 registros de análisis de riesgo, 713 registros de tasas de mortalidad y series históricas de morbimortalidad (2008–2017) provenientes del portal de datos abiertos del AMVA, así como el flujo continuo de lecturas de la red de estaciones del SIATA. El proceso garantiza la disponibilidad e integridad del 100% de los registros históricos procesados, eliminando la volatilidad de las lecturas ambientales mediante la persistencia en la base de datos relacional. La Tabla 1 resume la caracterización y el volumen de la información consolidada en el sistema. 

Tabla 1. Inventario y caracterización finales de los conjuntos de datos integrados. 

 

Fuente / Dataset 

Volumen Procesado 

Frecuencia / Cobertura 

Indicador / Variable Clave Servida 

API SIATA 

Continuo 

Actualización cada 2 min 

Concentración actual de PM2.5 e ICA. 

Análisis de Riesgo 

1,652 registros 

Histórico (2008–2017) 

Coeficiente epidemiológico beta e incremento de riesgo básico. 

Tasas de Mortalidad 

713 registros 

Histórico (2008–2017) 

Tasas de mortalidad respiratoria por municipio y sexo. 

Morbimortalidad 

Serie consolidada 

10 municipios del AMVA 

Conteo de casos de enfermedades y defunciones según la CIE-10. 

 

 

El resultado central del modelo relacional en PostgreSQL fue la creación funcional de la vista vista_riesgo_integrado, que unifica dinámicamente las lecturas de cada estación de monitoreo ambiental con los datos epidemiológicos del municipio correspondiente, vinculando las concentraciones en tiempo real de PM2.5 con los coeficientes beta epidemiológicos históricos. 

La API REST implementada en FastAPI expone esta vista mediante endpoints parametrizados que devuelven respuestas estructuradas en formato JSON. La Tabla 2 describe los campos y parámetros expuestos por la vista consolidada. 

Tabla 2. Campos consolidados y métricas servidas en la vista vista_riesgo_integrado. 

 

Campo en Base de Datos 

Tipo de Dato 

Origen de la Información 

Utilidad estimada 


municipio 

VARCHAR 

Dimensión Municipios 

Filtro territorial y delimitación geográfica 

pm25_actual / categoria_ica 

FLOAT / VARCHAR 

API SIATA en vivo 

Despliegue de estado ambiental y mapa de calor 

coeficiente_riesgo beta 

FLOAT 

Dataset Análisis de Riesgo 

Parámetro matemático para la calculadora de riesgo 

incremento_riesgo_pct_actual	FLOAT	Cálculo relacional derivado	Estimación del riesgo epidemiológico en tiempo 

real. 

 

 

 

Conclusiones 

 

El presente trabajo cumplió el objetivo planteado al diseñar e implementar un pipeline de integración de datos (ETL), logrando fusionar en tiempo real las mediciones de PM2.5 de la red SIATA con los registros epidemiológicos históricos (2008–2017) del AMVA. Entre los aportes se destacan el desarrollo de una arquitectura de datos automatizada en Python, la estructuración de un modelo relacional en PostgreSQL mediante la vista vista_riesgo_integrado. 

Esta propuesta contribuye a encontrar una alternativa de solución a la fragmentación entre la información ambiental y la sanitaria, transformando lecturas generales en un Índice de Riesgo Local que estima el incremento del riesgo epidemiológico de forma personalizada según el municipio, el sexo, el grupo diagnóstico y el rango etario. La principal limitación radica en la disponibilidad y el acceso a datos epidemiológicos actualizados. Como trabajo futuro, se plantea consultar fuentes de datos de las series de salud con datos recientes, incorporar la ingesta activa de datos de sensores ciudadanos PurpleAir aplicando los algoritmos de mitigación de sesgo por humedad desarrollados, e integrar modelos predictivos de aprendizaje automático para anticipar picos de contaminación y sus efectos diferidos en las consultas hospitalarias. 

 

Referencias 

 

J. S. Parra-Sánchez, A. I. Oviedo-Carrascal, y F. O. Amaya-Fernández, “Analítica de datos: incidencia de la contaminación ambiental en la salud pública en Medellín (Colombia)”, Revista de Salud Pública, vol. 22, núm. 6, pp. 609–617, nov. 2020, doi: 10.15446/RSAP.V22N6.78985. 

H. Amini et al., “Two Decades of Air Pollution Health Risk Assessment: Insights From the Use of WHO’s AirQ and AirQ+ Tools”, Public Health Reviews, vol. 45, 2024, doi: 10.3389/PHRS.2024.1606969/FULL. 

X. T. Xiao Tang et al., “A Six-year long High-resolution Air Quality Reanalysis Dataset over China from 2013 to 2018”, Science Data Bank Datasets, doi: 10.11922/SCIENCEDB.00053. 

R. Sserunjogi et al., “Design and Evaluation of a Scalable Data Pipeline for AI-Driven Air Quality Monitoring in Low-Resource Settings”, en 34th International Conference on 
Software Engineering and Data Engineering, Springer Science and Business Media Deutschland GmbH, ago. 2025, pp. 212–231. doi: 10.1007/978-3-032-08649-5_14. 

P. Mudu, M. Krzyżanowski, y C. Gapp, “Evaluación de impacto en salud de la contaminación del aire: Manual de introducción a AirQ+”, 2023. 

P. Ferrer-Cid, J. A. Paredes-Ahumada, X. Allka, M. Guerrero-Zapata, J. M. Barcelo-Ordinas, y J. Garcia-Vidal, “A Data-Driven Framework for Air Quality Sensor Networks”, IEEE Internet of Things Magazine, vol. 7, núm. 1, pp. 128–134, ene. 2024, doi: 10.1109/IOTM.001.2300112. 

R. Sserunjogi et al., “Design and Evaluation of a Scalable Data Pipeline for AI-Driven Air Quality Monitoring in Low-Resource Settings”, el 20 de agosto de 2025, Springer Science and Business Media Deutschland GmbH. doi: 10.1007/978-3-032-08649-5_14. 

J. G. Piñeros-Jiménez et al., “Distribución espacial de la morbimortalidad atribuible a la contaminación del aire por PM2.5 en Medellín (Colombia), 2010-2016”, Revista Facultad Nacional de Salud Pública, vol. 40, núm. 2, may 2022, doi: 10.17533/UDEA.RFNSP.E346589. 

Universidad Pontificia Bolivariana, “Promesa por la vida saludable de los niños y niñas | UPB”. Consultado: el 24 de septiembre de 2026. [En línea]. Disponible en: https://www.upb.edu.co/ss/Satellite?c=UPB_Noticia&cid=1464271691375&pagename=U PB_PortalPrincipal%2FUPB_Noticia%2FGRID_DETALLE_NOTICIA 

“SIATA - Sistema de Alerta Temprana”. Consultado: el 24 de septiembre de 2026. [En línea]. Disponible en: https://siata.gov.co/boletinnp.php 

“PurpleAir Sensors Functional Overview - Sensors - PurpleAir Community”. Consultado: el 24 de septiembre de 2026. [En línea]. Disponible en: https://community.purpleair.com/t/purpleair-sensors-functional-overview/150 