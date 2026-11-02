Evaluación Final -Proyecto de Curso
Nombre de la
asignatura Adquisición e Integración de Datos
Nombre de
unidad Exploración e integración de datos
Nombre de la
actividad Diseño del proceso de integración para solucionar un caso de estudio.
Objetivo de la
actividad
Diseñar un proceso de adquisición, digitalización, codificación e integración de
datos para resolver un caso de la industria o de la vida real, incluyendo la
simulación de datos de una fuente primaria (tipo sensor) y su integración con al
menos otras dos fuentes heterogéneas consideradas en un flujo de datos definido
por el equipo, y utilizando Python, OpenRefine y/o Power Query como
herramientas de integración.
Fecha de
entrega de la
actividad
Curso martes: 01 de junio de 2026
Curso viernes: 04 de junio de 2026
1 Estrategia de conformación de equipos de trabajo:
A partir de los equipos conformado para el proyecto de curso (mínimo dos y máximo tres personas) se
desarrolla la actividad propuesta. Quién realice la actividad de manera individual tendrá una calificación
sobre 4.0. A continuación, se establecen las acciones a seguir.
1.1 Integridad académica
La documentación del informe deberá ser inédita, es decir escrita por las/os integrantes del equipo.
Soporten sus argumentos y datos citando las referencias de fuentes consultadas. No usar herramientas
de Inteligencia Artificial Generativa (GenIA, por su sigla en inglés) para la construcción de texto en el
documento técnico. Si usan una herramienta de GenIA para construir diagramas o las presentaciones
deben anexar el Prompt y citar en el documento la herramienta, la referencia al uso de la herramienta
se incluye en el apartado de referencias. Eviten copiar y pegar texto de otros trabajos lo cual podría
acabar en un llamado de atención con copia a su hoja de vida por alto % de similitud o plagio.
Programa de Ingeniería en Ciencia de Datos
Institución Universitaria ITM
2 Parámetros de la actividad
2.1 INFORME FINAL
Atender las recomendaciones de la entrega anterior (segunda actividad evaluativa) y utilizar el formato
de informe propuesto. Este informe deberá seguir las siguientes indicaciones.
SECCIÓN Ítem Descripción ALCANCE DE LA PROPUESTA Portada
▪ Título coherente con el objetivo y con máximo 15 palabras
▪ Autores con nombre completo y número de carne.
▪ Nombre del curso y del programa académico.
▪ Fecha de entrega
Problema o situación
de interés
▪ Explicar el contexto del problema ¿Cuáles son sus causas y
consecuencias? Los diagramas de Ishikawa y 5 por qué elaborados y
ajustados deberán incluirse en la carpeta de anexos.
▪ Justificar la necesidad de solucionarlo desde un proyecto de ciencia
de datos.
▪ Argumentar por que se requiere la adquisición e integración de tres
fuentes de datos, una fuente primaria (simulando un sensor) y dos
fuentes de datos, como archivos o tablas generadas por web
Scraping.
Trabajo
relacionad
o
▪ Describir al menos tres trabajos realizados previamente para
resolver con ciencia de datos una situación similar al caso que
trabajan. Citar las referencias.
▪ Explicar de manera clara y precisa como los trabajos indicados
ayudan a entender y/o solucionar el caso de estudio.
Objetivo de
la propuesta
de solución
▪ Definir un objetivo general para el ámbito de la ingeniería en ciencia
de datos. Se debe cumplir con las características de un objetivo
SMART, es decir, el objetivo debe ser Específico, Medible,
Alcanzable, Relevante.
▪ Debe responder las preguntas ¿Qué se va a hacer? ¿Cómo? y ¿Para
qué? ¿Qué resultado cuantificable esperan lograr?
Variable(
s) por
adquirir
▪ Describir la(s) magnitud(es) física(s) o variable(s) específica(s) que
necesitan ser medidas directamente de las fuentes primarias
(simulando el sensor, archivos o encuestas) para la resolución del
problema o mejora de la situación de interés.
IDENTIFICACIÓN DE FUENTES DE DATOS
Descripción y Justificación
de las Fuentes de Datos
▪ Describir para cada fuente de datos (una primaria- sensor, otras dos
complementarias) por qué se requiere, cómo está estructurada, cuál
es la variable más importante y cómo contribuye a la solución.
▪ Describir en un párrafo (No en una tabla por campo) por qué la
integración de estas fuentes de datos contribuye a facilitar la
solución.
▪ Las tres fuentes deben ser de diferentes tipos. Al menos una fuente
complementaria debe obtenerse conceptualmente de internet (web
Scraping, descarga de tablas automática de un sitio web, etc.) La
otra puede ser un archivo local (CSV, Excel, etc.) o una simulación de
base de datos simple (datos sintéticos).
Estructuració
n de los
datos
▪ Presentar la estructura en tabla de los datos que serán recopilados
para su almacenamiento y procesamiento.
▪ Elaborar el diccionario de datos para cada una de las fuentes de
datos e incluirlos en la carpeta de anexos. En la carpeta de Anexos
incluya los archivos y los diccionarios de datos de las fuentes de
datos.
Programa de Ingeniería en Ciencia de Datos
Institución Universitaria ITM
SECCIÓN Ítem Descripción Proceso Conceptual de Digitalizació n y Codificación
▪ Describir el tipo de sensor o transductor que conceptualmente
utilizarían
▪ Explicar y justificar por qué ese tipo de sensor es adecuado para
capturar la variable en el contexto de su problema.
▪ Ilustrar en un diagramar el proceso mediante el cual la magnitud
física se convierte en un dato digital útil.
DISEÑO DEL PROCESO DE INTEGRACIÓN
Contexto de Integración
▪ Describir cómo se realizará el proceso de integración de las
diferentes fuentes de datos (la simulada del sensor y las adicionales)
para la solución del problema. Indicar si usarán, por ejemplo, JOIN,
o MERGE.
▪ Describir dónde se almacenará el resultado final con los datos
integrados (una nueva hoja en Excel, un archivo CSV final, un
DataFrame listo para análisis). ¿Cuál será la estructura final de la
tabla integrada?
▪ Explicar como la integración de las fuentes aporta al análisis y la
solución del problema.
Diagrama de Flujo
de ETL
▪ Crear y describir un diagrama de flujo conceptual que muestre como
interactúan las tres fuentes de datos identificadas y que represente
el camino (pipeline) que siguen los datos en su adquisición (si aplica
conceptualmente), integración, y corrección de errores, hasta llegar
a su destino final (tabla, archivo, gráfico) donde serán utilizados para
resolver el problema.
▪ Citar la herramienta utilizada para la creación del diagrama y si aplica
en un Anexo reportar el prompt.
Herramientas
para la
integración
de datos
Describir cual fue la herramienta elegida para el proceso de
integración ETL y porqué fue la adecuada para la solución que están
diseñando.
VALIDACIÓN Y APLICACIÓN
Transformación
de los datos
▪ Describir y reportar evidencias del perfilamiento de las tres fuentes
de datos con Python, Open Refine y/o Power Query.
▪ Describir al menos cinco transformaciones realizadas.
▪ Describir la creación de al menos dos columnas adicionales en una
de las fuentes de datos.
Resultado de la
integración
▪ Explicar cómo fue el pipeline de los datos en el proyecto y el
resultado de la integración de los datos.
▪ Incluir una evidencia del resultado de integración. En la carpeta de
anexos agregue el notebook y archivo final con los datos ya
integrados de todas las fuentes.
▪ Explicar cómo el proceso diseñado (desde la adquisición
conceptual hasta la integración práctica) y la tabla de datos
integrada resultante contribuye en la solución del problema
(objetivo SMART) de adquisición e integración planteado
inicialmente.
Programa de Ingeniería en Ciencia de Datos
Institución Universitaria ITM
SECCIÓN Ítem Descripción CONCLUSIONES
▪ No presentar un resumen del proyecto.
▪ Concluir en sus palabras sobre las lecciones aprendidas del equipo durante el
desarrollo del proyecto. No usar IA Generativa.Presentar las conclusiones resultado
de la discusión del aprendizaje del diseño del proceso de adquisición e integración
de datos, y como estos procesos aportan a la solución del casi seleccionado.
▪ Concluir sobre el proceso de uso de Python, OpenRefine y Power Query en las
transformaciones, qué funciono o no.
REFEREN
CIAS
Relacionar al menos cinco referencias académicas que sean obtenidas de las bases de
datos institucionales y que se encuentren citadas en el documento utilizando el estilo
IEEE. Se deben citar las referencias en el documento.
2.2 PRESENTACIÓN DEL PROYECTO
El objetivo de la presentación será convencer de que su solución es eficiente y a través de la adquisición
e integración de datos se contribuye a solucionar el problema.
I. La sustentación en equipo será de manera oral y presencial, apoyándose en un archivo o un
enlace con el acceso a la aplicación on-line, asegurando que sea visible a externos.
II. El archivo de apoyo a la sustentación del trabajo deberá nombrarse así:
AE4_AP_EquipoX_DDMMAAAA.
III. La duración máxima de la presentación será de siete minutos por equipo. El archivo de apoyo
deberá contar con máximo nueve diapositivas que incluyen la portada y referencias. Se debe
evidenciar:
▪ El problema (datos, causas, consecuencias).
▪ Objetivo de la solución
▪ Como los datos contribuyen a solucionar el problema.
▪ El diseño del pipeline de datos, precisando las fuentes de datos y el resultado de su
integración (pueden hacer una demostración)
▪ Lecciones aprendidas y conclusiones.
2.3 ENTREGA DE EVIDENCIAS
IV. Presentar en una carpeta .ZIP que contenga:
▪ El documento técnico en formato Word u otro procesador de texto de máximo quince
páginas utilizando el formato anexo a la actividad que contenga la descripción de los
numerales previos. El archivo deberá nombrarse así: AE4_EquipoX_DDMMAAAA.
▪ Carpeta de Anexos que incluya:
oAnexos de figuras del problema.
oArchivos de las fuentes de datos antes y después de las transformaciones.
oArchivos de la integración (Notebook con los scripts de Python, archivos de
OpenRefine o archivo en Excel con los pasos seguidos en PowerQuery).
V. Soporte datos y argumentos citando las referencias de fuentes consultadas. Realiza la citación
en el estilo IEEE). El listado de referencias no se cuenta como parte de las páginas del escrito.
Pueden consultar los siguientes enlaces que explican cómo utilizar este estilo de citación:
https://biblioguias.uam.es/citar/estilo_ieee
https://www.youtube.com/watch?v=JGDZiCwTQXU
VI. Se recibirán los trabajos de cada equipo en la plataforma C-VIRTUAL. Solo una(o) de las(os)
estudiantes debe subir los archivos. No olviden relacionar en el formato de entrega el nombre
de todas(os) las(os) integrantes. En el caso de que no se cuente habilitada la plataforma,
deberán remitir los archivos al correo electrónico
mariutsiosorio9880@correo.itm.edu.co. En este caso, solo un/a estudiante debe realizar
la entrega por todo el equipo de trabajo y deberá copiar el mensaje a sus compañeras/os.
Programa de Ingeniería en Ciencia de Datos
Institución Universitaria ITM
2.4 EVALUACIÓN
I. El informe tiene un peso del 30% en la calificación. Se evaluará el diseño propuesto, la
profundidad del análisis, la calidad y detalle de las justificaciones de cada decisión (problema,
fuentes, sensor, enfoque de integración, pasos de transformación, etc.), la precisión en la
descripción de los procesos de integración y corrección de errores, la calidad de la simulación
de datos, y la claridad de la evidencia de implementación proporcionada (pantallazos o código
comentado). También se califica la calidad del documento (formato, ortografía y redacción) y la
pertinencia de las conclusiones.
II. La presentación en equipo tiene un peso del 70% en la calificación. Se evaluará las habilidades
de comunicación de manera clara y precisa y que en equipo se cubra en el tiempo los puntos
clave indicados en el numeral 2.3. Se podrá preguntar a cualquier miembro del proyecto. La
calificación en este apartado podrá ser individual.
Criterio Descripción %
Informe
anexos
Present. Oral
/sustentación
Definición
del Problema
y Objetivo
Problema claro y soportado en datos y
referencia. Objetivo SMART y variables
coherentes
30
30% 70%
Diseño
Conceptual
de
Adquisición
Sensor adecuado, diagrama claro, descripción
proceso digitalización/codificación coherente,
simulación de datos sensor incluida y bien
definida.
Identificación
Fuentes
Adicionales
Integración de al menos tres fuentes relevantes
para solucionar el problema.
Diseño
Proceso
Integración
Selección enfoque/herramienta justificada,
diagrama flujo claro, pasos bien detallados,
lógica correcta.
30
Validación y
Aplicación
Muestra resultado integrado, explica
claramente cómo el proceso/resultado
resuelve el problema.
20
Presentación
y
Conclusiones
Documento organizado, cumple con el
formato, ortografía, redacción, citación
correcta de fuentes y Conclusiones pertinentes
sobre el proceso
20
TOTAL 100