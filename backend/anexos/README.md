# Anexos del proyecto

Esta carpeta reúne todos los datos, notebooks y documentos de apoyo del
proyecto, separados por tipo para que sean fáciles de encontrar y explicar.

## Estructura

```text
anexos/
├── datos/
│   ├── crudos/         # 4 CSV originales 2008–2017 (entrada del pipeline)
│   ├── limpios/        # Salidas de limpieza de los históricos
│   └── integrados/     # datos_integrados.csv con el resultado del cruce
├── notebooks/          # Notebooks de EDA, limpieza e integración
├── documentos/
│   ├── contexto/       # Insumos y contexto usados para trabajar con IA
│   └── generados/      # Documentos producidos (metodología, guía, plan, etc.)
└── recursos/           # Imágenes y documento original de la idea
```

## Contenido por carpeta

### `datos/crudos/`
Archivos de entrada del pipeline, sin modificar:

- `AnalisisRiesgo_20082017.csv`
- `EnfermedadesCalculadas_2008-2017.csv`
- `TasaMortalidad_2008-2017.csv`
- `DefunsionesCalculadas_2008-2017.csv`

El pipeline los lee desde aquí (ver `backend/etl/configuracion/settings.py`).

### `datos/limpios/`
Resultados de la fase de transformación:

- `DATOS_LIMPIOS.csv`
- `DefunsionesCalculadas_LIMPIO.csv`

### `datos/integrados/`
- `datos_integrados.csv`: 2.402 registros que cruzan las tres fuentes.

### `notebooks/`
- `limpieza_AnalisisRiesgo.ipynb`
- `EnfermedadesCalculadas_2008_2017.ipynb`
- `Tasa_Mortalidad.ipynb`
- `difsionescalculadas (2).ipynb`
- `integracion_datos.ipynb`

### `documentos/contexto/`
Insumos y contexto del proyecto:

- `contexto.md`
- `fundamentacion.md`
- `perfilamiento_fuentes.md`
- `herramienta_integracion_etl.md`
- `propuesta_dashboard_salud_calidad_aire.md`
- `documento_evaluado.md`
- `comentarios_evaluadores.md`
- `indicaciones_entrega_final.md`
- `documentacion_idea_proyecto.docx`

### `documentos/generados/`
Documentos producidos durante el proyecto:

- `metodologia_reproducible.md`
- `guia_explicacion_codigo.md`
- `plan_mejoramiento.md`
- `guion_pitch.md`
- `diagrama_flujo.md`
- `resultado_integracion.md`
- `analisis_exploratorio_api_calidad_aire.md`

### `recursos/`
- `calidad_aire.png`
- `sisaire.png`
