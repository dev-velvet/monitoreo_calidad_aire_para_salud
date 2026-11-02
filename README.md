# Sistema de Monitoreo de Calidad del Aire y Salud Pública (Valle de Aburrá)

Proyecto de **Integración y Adquisición de Datos** (Ciencia de Datos - ITM).
Implementa un pipeline **ETL** que integra datos históricos de salud pública
(mortalidad, morbilidad, defunciones y coeficientes de riesgo) con mediciones de
calidad del aire en tiempo real obtenidas de la API de **SIATA**. El resultado se
almacena en **PostgreSQL**, se expone mediante una **API REST (FastAPI)** y se
consume en un dashboard interactivo.

---

## Documentación clave

| Documento | Contenido |
|-----------|-----------|
| [`backend/anexos/README.md`](backend/anexos/README.md) | Índice y organización de todos los anexos |
| [`backend/anexos/documentos/generados/metodologia_reproducible.md`](backend/anexos/documentos/generados/metodologia_reproducible.md) | Metodología reescrita y reproducible (para el paper) |
| [`backend/anexos/documentos/generados/guia_explicacion_codigo.md`](backend/anexos/documentos/generados/guia_explicacion_codigo.md) | Cómo explicar el código y su relación con la investigación |
| [`backend/anexos/documentos/generados/plan_mejoramiento.md`](backend/anexos/documentos/generados/plan_mejoramiento.md) | Plan de respuesta a los comentarios de los evaluadores |
| [`backend/anexos/documentos/generados/diagrama_flujo.md`](backend/anexos/documentos/generados/diagrama_flujo.md) | Diagrama de flujo ETL (Mermaid) |
| [`backend/anexos/documentos/generados/guion_pitch.md`](backend/anexos/documentos/generados/guion_pitch.md) | Guion de la presentación oral |

---

## Arquitectura del pipeline

1. **Extracción**
   - 4 CSV históricos (2008–2017) del portal de datos abiertos del AMVA.
   - Feed KML de PM2.5 de la API de **SIATA**.
2. **Transformación**
   - Normalización de municipios y grupos de edad.
   - Corrección de separadores decimales, filtrado de `-999`, eliminación de
     duplicados y validación de calidad.
3. **Integración y carga**
   - Modelo estrella en PostgreSQL: dimensiones (`municipios`, `contaminantes`,
     `grupos_diagnosticos`) y hechos (`analisis_riesgo`, `enfermedades`,
     `tasa_mortalidad`, `defunciones`, `mediciones_siata`).
   - Vista materializada `vista_riesgo_integrado` con el JOIN estación→municipio y
     el cálculo del incremento de riesgo `ΔR = (e^(β·PM2.5/10) − 1) × 100`.
4. **Automatización**
   - `etl/scheduler.py` actualiza la fuente primaria cada hora (o cada 10 s en
     modo demostración).

---

## Estructura del proyecto

```text
monitoreo_calidad_aire_para_salud/
├── README.md
│
└── backend/
    ├── etl/                    # Pipeline ETL por fases
    │   ├── configuracion/      # settings.py, diccionarios.py
    │   ├── extraccion/         # siata_api.py
    │   ├── transformacion/     # limpieza_*.py, calidad_datos.py
    │   ├── carga/              # conexion, esquema, dimensiones, hechos, siata, vista
    │   ├── pipeline.py         # Orquestador ETL
    │   └── scheduler.py        # Daemon de actualización
    ├── app/                    # API FastAPI (routers: municipios, siata, salud)
    ├── consultas/              # consultas_validacion.sql
    ├── anexos/                 # Todos los anexos (ver anexos/README.md)
    │   ├── datos/
    │   │   ├── crudos/         # 4 CSV originales 2008–2017
    │   │   ├── limpios/        # Salidas de limpieza
    │   │   └── integrados/     # datos_integrados.csv
    │   ├── notebooks/          # Notebooks EDA e integración
    │   ├── documentos/
    │   │   ├── contexto/       # Insumos y contexto para la IA
    │   │   └── generados/      # Documentos producidos (metodología, guía, plan...)
    │   └── recursos/           # Imágenes y documento original
    ├── check_data.py           # Verificación rápida de conteos
    ├── requirements.txt
    └── pyproject.toml
```

---

## Instalación y configuración

### 1. Requisitos

- Python 3.12 o superior.
- PostgreSQL 14 o superior (local o en la nube: Neon.tech / Render).

### 2. Dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 3. Base de datos

Configura la conexión mediante variables de entorno (archivo `.env` en
`backend/`):

```env
# Opción nube (recomendada para despliegue)
DATABASE_URL=postgresql://usuario:password@host:puerto/base

# Opción local
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=calidad_aire_salud
```

No hay credenciales embebidas en el código; se leen con `python-dotenv`.

---

## Ejecución

Desde la carpeta `backend/`:

```bash
# 1. Pipeline ETL completo (crea BD, esquema, carga históricos y SIATA)
python -m etl.pipeline

# 2. Actualización periódica de SIATA
python -m etl.scheduler          # producción: cada 1 hora
python -m etl.scheduler --demo   # demostración: cada 10 segundos

# 3. API REST
uvicorn app.main:app --reload --port 8000
# Documentación interactiva: http://localhost:8000/docs
```

---

## Validación

```bash
# Conteos por tabla
python check_data.py
```

Además, ejecuta las consultas de
[`backend/consultas/consultas_validacion.sql`](backend/consultas/consultas_validacion.sql)
para verificar integridad referencial (cero registros huérfanos) y consistencia
de las tablas de hechos.

---

## Resultado de la integración

- `vista_riesgo_integrado`: cruza la última lectura de PM2.5 por estación con los
  coeficientes β históricos del municipio, sexo, grupo etario y diagnóstico.
- `backend/anexos/datos/integrados/datos_integrados.csv`: evidencia exportada del resultado.
- `backend/anexos/datos/limpios/DATOS_LIMPIOS.csv` y
  `backend/anexos/datos/limpios/DefunsionesCalculadas_LIMPIO.csv`: salidas limpias
  de los históricos de riesgo y defunciones.
- API REST con endpoints de catálogos, mediciones actuales y calculadora de
  riesgo personalizado (`/api/salud/riesgo-cruzado`).

---

## Roles del equipo

- **Mariana**: arquitectura de la base de datos, API SIATA, conector PostgreSQL,
  orquestador y scheduler.
- **Yeison**: limpieza y normalización de los datasets de riesgo y morbilidad.
- **Integrante 1**: narrativa del problema, dashboard y presentación.
