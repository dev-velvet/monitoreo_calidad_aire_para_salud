# Guion AireSalud: Sencillo, Impactante y Fácil de Recordar (7 Minutos)
**Asignatura:** Adquisición e Integración de Datos (ITM)

---

## Roles y Estructura del Equipo
* **Integrante 1 (Especialista en Datos/ETL y UI/UX):** El narrador principal. Hace la introducción, maneja la pantalla, explica el problema y realiza el cierre emocional.
* **Integrante 2 (Yeison - Especialista en Datos/ETL):** El detective de datos. Explica de dónde vienen los datos (ETL) de forma sencilla y metafórica.
* **Integrante 3 (Mariana - Desarrollador Backend/API):** El cerebro del sistema. Explica cómo la API y el modelo matemático conectan todo tras bambalinas.

---

### 1. INTRODUCCIÓN Y PROBLEMA (0:00 - 1:15)

* **[0:00 - 0:20] Integrante 1 (Especialista en Datos/ETL y UI/UX):**  
  > *"¿Sabían que en el Valle de Aburrá, durante una contingencia ambiental, salir a respirar equivale a fumarse tres cigarrillos al día? Y lo peor: le da igual si tienes 5 o 80 años. La contaminación por material particulado PM2.5 no es solo humo en el aire; son personas reales terminando en salas de urgencias porque sus pulmones no aguantan más."*
  
  * **[ACCIÓN EN PANTALLA]:**  
    * El Integrante 1 abre la aplicación en vivo (https://airwise-health.onrender.com).
    * Pasa el cursor sobre el logo **AireSalud** y señala el cintillo superior de `SIATA · en vivo`.

* **[0:20 - 0:50] Integrante 1 (Especialista en Datos/ETL y UI/UX):**  
  > *"Las aplicaciones del clima nos muestran caritas felices o alertas genéricas de color amarillo o naranja. Pero eso no nos dice nada útil. No es lo mismo respirar en el centro de Medellín que en Sabaneta, ni le afecta igual a un bebé que a nuestros abuelos. Faltaba una herramienta que uniera los sensores de la ciudad con los historiales médicos de los hospitales. Por eso creamos **AireSalud**."*
  
  * **[ACCIÓN EN PANTALLA]:**  
    * El Integrante 1 hace un scroll suave hacia abajo mostrando las tres secciones: **Sección A (Mapa)**, **Sección B (Calculadora)** y **Sección C (Gráficos históricos)**, y vuelve a subir al mapa.

* **[0:50 - 1:15] Integrante 1 (Especialista en Datos/ETL y UI/UX):**  
  > *"Nuestra solución hace algo único: toma la contaminación de la calle en este preciso instante y la traduce en un riesgo de salud real y personalizado para ti. Pasamos de datos aburridos a información que salva vidas."*

---

### 2. LA SOLUCIÓN Y VALOR AGREGADO (1:15 - 2:30)

* **[1:15 - 1:45] Integrante 1 (Especialista en Datos/ETL y UI/UX):**  
  > *"En nuestra **Sección A** vemos el Valle de Aburrá hoy. Tenemos 23 estaciones midiendo el aire. En este momento, el promedio regional es de `16.5 microgramos` y la zona más crítica marca `23.0` en Medellín. Pero para traducir esto a la salud humana, necesitamos viajar en el tiempo. Yeison nos contará cómo lo logramos."*
  
  * **[ACCIÓN EN PANTALLA]:**  
    * El Integrante 1 apunta a las tarjetas de KPI arriba: **Promedio regional** y **Estación más crítica**.

* **[1:45 - 2:30] Integrante 2 (Yeison - Especialista en Datos/ETL):**  
  > *"Gracias. Para lograrlo, unimos tres piezas de un rompecabezas. La primera es la historia de nuestra salud: analizamos más de 10 años de registros hospitalarios (2008-2017) de la región. Esto nos dijo exactamente cuántas personas enfermaron o fallecieron en el pasado debido al aire."*
  
  * **[ACCIÓN EN PANTALLA]:**  
    * El Integrante 1 baja a la **Sección C (Gráficos)**.
    * Yeison habla mientras el Integrante 1 señala la gráfica de líneas y el ranking de municipios más afectados.
  
  > *"La segunda pieza es el presente: las mediciones que hace SIATA en tiempo real. Y la tercera pieza son los catálogos de municipios. Al juntar el pasado con el presente, podemos predecir el impacto de hoy."*

---

### 3. INGENIERÍA DE DATOS (ETL) (2:30 - 4:15)

* **[2:30 - 3:15] Integrante 2 (Yeison - Especialista en Datos/ETL):**  
  > *"Pero esos datos del pasado estaban en archivos planos, desordenados y con nombres mal escritos. Usamos Python para limpiarlos y ordenarlos en una base de datos organizada en la nube. Hicimos que los datos 'hablaran el mismo idioma'."*

* **[3:15 - 3:45] Integrante 2 (Yeison - Especialista en Datos/ETL):**  
  > *"Para el presente, creamos un robot que se conecta a SIATA cada hora, descarga los reportes de los sensores y descarta lecturas erróneas de estaciones en mantenimiento. Así garantizamos que la información del mapa sea fresca y real."*
  
  * **[ACCIÓN EN PANTALLA]:**  
    * El Integrante 1 sube al mapa y hace clic en una estación para abrir el popup con los datos de PM2.5 actuales.

* **[3:45 - 4:15] Integrante 2 (Yeison - Especialista en Datos/ETL):**  
  > *"Además, fuimos inteligentes: en lugar de amarrar rígidamente los sensores de la ciudad a nuestra base de datos, los conectamos mediante coincidencias de texto. Si el gobierno cambia una estación de lugar o le cambia el nombre, nuestro sistema se adapta solo, sin romperse. Ahora Mariana les explicará cómo el sistema procesa todo esto."*

---

### 4. ARQUITECTURA DE ENDPOINTS Y API (4:15 - 5:45)

* **[4:15 - 4:45] Integrante 3 (Mariana - Desarrollador Backend/API):**  
  > *"Para conectar esta base de datos con la pantalla que ven, creamos una API en FastAPI. Es como el mesero de un restaurante: toma tu pedido en la pantalla, va a la cocina (la base de datos) y te trae el plato listo. Por ejemplo, los listados de municipios y edades se llenan automáticamente desde ahí para que el usuario no tenga que escribir nada a mano."*
  
  * **[ACCIÓN EN PANTALLA]:**  
    * El Integrante 1 baja a la **Sección B (Calculadora)** y hace clic en el dropdown de Municipios mostrando las opciones dinámicas.

* **[4:45 - 5:15] Integrante 3 (Mariana - Desarrollador Backend/API):**  
  > *"En el mapa, nos aseguramos de que cada estación muestre estrictamente su lectura más reciente. Hacemos un filtro rápido en la base de datos para que la pantalla cargue en menos de un parpadeo y sin repetir información."*

* **[5:15 - 5:45] Integrante 3 (Mariana - Desarrollador Backend/API):**  
  > *"Pero nuestro mayor logro es el motor de riesgo cruzado. Cuando el usuario ingresa sus datos y presiona calcular, el sistema busca el sensor de su municipio, y si por algún motivo ese sensor no responde, el sistema calcula automáticamente un promedio regional como respaldo. Luego, toma la contaminación actual, la cruza con la sensibilidad del cuerpo para ese grupo de edad y sexo, y aplica una fórmula de la Organización Mundial de la Salud para darte tu riesgo exacto."*
  
  * **[ACCIÓN EN PANTALLA]:**  
    * En la calculadora, el Integrante 1 selecciona:
      * **Municipio:** `Sabaneta`
      * **Edad:** `68`
      * **Sexo:** `Femenino`
    * Hace clic en **Calcular riesgo**.
    * La pantalla derecha muestra de inmediato los incrementos en porcentajes de riesgo.

---

### 5. CONCLUSIÓN Y CIERRE (5:45 - 7:00)

* **[5:45 - 6:15] Integrante 1 (Especialista en Datos/ETL y UI/UX):**  
  > *"Miren el resultado: una mujer de 68 años en Sabaneta, con el aire que se respira hoy, tiene un incremento del `4.12%` en el riesgo de terminar en el hospital por una infección pulmonar. Esto ya no es un dato abstracto; es una alerta real."*
  
  * **[ACCIÓN EN PANTALLA]:**  
    * El Integrante 1 señala los porcentajes de riesgo recién calculados con el cursor.

* **[6:15 - 6:45] Integrante 1 (Especialista en Datos/ETL y UI/UX):**  
  > *"Con AireSalud, un alcalde puede saber a qué hospital mandar más recursos según la contaminación del día, y una madre puede decidir si es seguro llevar a su hijo al parque. Transformamos millones de filas de datos complejos en decisiones cotidianas."*

* **[6:45 - 7:00] Integrante 1 (Especialista en Datos/ETL y UI/UX):**  
  > *"Este proyecto une el análisis de datos, el monitoreo en tiempo real y la salud pública para proteger la vida en el Valle de Aburrá. Muchas gracias, y quedamos atentos a sus preguntas."*
  
  * **[ACCIÓN EN PANTALLA]:**  
    * Deja la pantalla fija en los resultados de la calculadora.
