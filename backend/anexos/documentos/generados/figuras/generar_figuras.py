"""
Generador de Figuras Científicas en Alta Resolución (300 DPI)
Proyecto: Monitoreo de Calidad del Aire y Salud Pública - Valle de Aburrá
Simposio de Ingeniería ITM 2026
"""

import os
import sys

# Configurar directorio temporal de caché para matplotlib
os.environ["MPLCONFIGDIR"] = os.path.join(os.environ.get("TEMP", "."), "mpl_cache")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def setup_canvas(width=14, height=8, dpi=300):
    fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")
    return fig, ax


def draw_box(ax, x, y, w, h, title, subtitle, items=None, bg="#F8FAFC", border="#64748B", title_color="#0F172A", title_fontsize=11):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.8,rounding_size=1.5",
                         edgecolor=border, facecolor=bg, linewidth=1.5)
    ax.add_patch(box)
    
    # Title
    ax.text(x + w/2, y + h - 2.8, title, ha="center", va="top", fontsize=title_fontsize, fontweight="bold", color=title_color)
    
    curr_y = y + h - 5.5
    if subtitle:
        ax.text(x + w/2, curr_y, subtitle, ha="center", va="top", fontsize=8.5, fontstyle="italic", color="#475569")
        curr_y -= 3.2
        
    if items:
        # Divider line
        ax.plot([x + 1.5, x + w - 1.5], [curr_y + 1, curr_y + 1], color=border, lw=0.8, alpha=0.5)
        curr_y -= 1.5
        for item in items:
            ax.text(x + 2, curr_y, item, ha="left", va="top", fontsize=8, color="#1E293B", family="sans-serif")
            curr_y -= 2.6


def draw_arrow(ax, x1, y1, x2, y2, label="", color="#334155", lw=1.8):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=14))
    if label:
        mid_x, mid_y = (x1 + x2)/2, (y1 + y2)/2
        ax.text(mid_x, mid_y + 1.2, label, ha="center", va="bottom", fontsize=7.5, fontweight="bold", color=color,
                bbox=dict(boxstyle="round,pad=0.2", fc="#FFFFFF", ec="none", alpha=0.85))


# ==============================================================================
# FIGURA 1: ARQUITECTURA GENERAL DEL SISTEMA
# ==============================================================================
def generar_figura_1():
    print("-> Generando Figura 1: Arquitectura del Sistema...")
    fig, ax = setup_canvas(width=15, height=8.5, dpi=300)
    
    # Encabezado
    ax.text(50, 96.5, "ARQUITECTURA INTEGRAL DE ADQUISICIÓN, INTEGRACIÓN Y VISUALIZACIÓN",
            ha="center", va="top", fontsize=13, fontweight="bold", color="#0F172A")
    ax.text(50, 93.5, "Plataforma AireSalud — Monitoreo de Calidad del Aire (PM2.5) y Morbilidad en el Valle de Aburrá",
            ha="center", va="top", fontsize=9.5, color="#475569")
    
    # Columnas: Fuentes (x:3), Backend/ETL (x:27), PostgreSQL (x:53), Frontend (x:76)
    
    # 1. FUENTES DE DATOS
    ax.text(14, 88, "FUENTES DE ENTRADA", ha="center", fontsize=10, fontweight="bold", color="#1E40AF")
    draw_box(ax, 3, 62, 22, 23, "API SIATA (En Vivo)", "Fuente Primaria — Telemetría",
             ["• Feed KML público en tiempo real", "• ~23 estaciones de monitoreo", "• Muestreo cada 2 minutos", "• PM2.5, coordenadas, fecha/hora"],
             bg="#EFF6FF", border="#3B82F6", title_color="#1D4ED8")
    
    draw_box(ax, 3, 34, 22, 25, "AMVA (Históricos 2008–2017)", "Fuente Secundaria — Epidemiología",
             ["• 4 datasets abiertos en CSV", "• Análisis de Riesgo (1.652 filas)", "• Morbilidad: Enf. respiratorias", "• Mortalidad y defunciones", "• Coeficientes epidemiológicos β"],
             bg="#EFF6FF", border="#3B82F6", title_color="#1D4ED8")

    draw_box(ax, 3, 9, 22, 22, "Datos.gov.co", "Catálogo Geodésico Oficial",
             ["• Dataset territorial de municipios", "• Coordenadas latitud / longitud", "• Respaldo en JSON local", "• Asignación geográfica de respaldo"],
             bg="#EFF6FF", border="#3B82F6", title_color="#1D4ED8")
             
    # 2. CAPA BACKEND & PIPELINE ETL
    ax.text(38, 88, "PIPELINE ETL & SERVICIOS REST", ha="center", fontsize=10, fontweight="bold", color="#065F46")
    draw_box(ax, 28, 56, 20, 29, "Extracción y Calidad", "etl/extraccion/ & etl/transformacion/",
             ["• HTTP GET asíncrono con timeout", "• Parser XML/KML sin namespaces", "• Filtro atípicos: -999 y <0 a NULL", "• Estandarización ICA Res. 2254", "• Fallback Haversine de municipios"],
             bg="#ECFDF5", border="#10B981", title_color="#047857")

    draw_box(ax, 28, 24, 20, 29, "Carga y Servicios API", "FastAPI (app/routers/) & Scheduler",
             ["• Hilo de fondo daemon continuo", "• Carga idempotente UPSERT", "• /api/siata/actual (DISTINCT ON)", "• /api/siata/promedio (regional)", "• /api/salud/riesgo-cruzado (ΔR)"],
             bg="#ECFDF5", border="#10B981", title_color="#047857")

    # 3. BASE DE DATOS POSTGRESQL
    ax.text(62, 88, "ALMACENAMIENTO RELACIONAL", ha="center", fontsize=10, fontweight="bold", color="#6B21A8")
    draw_box(ax, 51, 48, 22, 37, "PostgreSQL (Esquema Estrella)", "Neon.tech Cloud / Local",
             ["DIMENSIONES (Catálogos):",
              " • municipios (10 AMVA)",
              " • contaminantes (pm25, pm10, o3)",
              " • grupos_diagnosticos (CIE-10)",
              "TABLAS DE HECHOS:",
              " • mediciones_siata (en vivo)",
              " • analisis_riesgo (β, IC95%)",
              " • enfermedades (casos 2008–17)",
              " • defunciones (muertes)"],
             bg="#FAF5FF", border="#A855F7", title_color="#7E22CE")

    draw_box(ax, 51, 15, 22, 30, "Vista Materializada", "vista_riesgo_integrado",
             ["• CTE 1: DISTINCT ON última medición",
              "• CTE 2: JOIN normalizado estación-muni",
              "• Cruce en vivo con coeficientes β",
              "• Cálculo automático de ΔR en SQL:",
              "  ΔR = (exp(β · PM2.5/10) - 1) × 100",
              "• Refresco tras cada ciclo de ingesta"],
             bg="#FAF5FF", border="#A855F7", title_color="#7E22CE")

    # 4. CAPA DE PRESENTACIÓN / FRONTEND
    ax.text(87, 88, "CAPA DE VISUALIZACIÓN", ha="center", fontsize=10, fontweight="bold", color="#9A3412")
    draw_box(ax, 76, 59, 21, 26, "Sección A: Estado Actual", "AirMap.tsx + KpiCards",
             ["• Mapa interactivo Leaflet.js", "• Pines de estaciones con escala ICA", "• Tarjetas KPI en tiempo real", "• Promedio metropolitano y peor sensor"],
             bg="#FFF7ED", border="#F97316", title_color="#C2410C")

    draw_box(ax, 76, 32, 21, 24, "Sección B: Calculadora", "RiskCalculator.tsx",
             ["• Parametrización: municipio, edad, sexo", "• Cálculo de riesgo en tiempo real", "• Alertas automáticas de fallbacks", "• Incremento porcentual por patología"],
             bg="#FFF7ED", border="#F97316", title_color="#C2410C")

    draw_box(ax, 76, 7, 21, 22, "Sección C: Tendencias", "Recharts (LineChart)",
             ["• Curvas temporales de morbilidad", "• Evolución histórica de defunciones", "• Ranking de casos por municipio", "• Barras de impacto acumulado"],
             bg="#FFF7ED", border="#F97316", title_color="#C2410C")

    # Flechas de conexión
    draw_arrow(ax, 25, 73, 28, 73, "XML/KML")
    draw_arrow(ax, 25, 46, 28, 62, "CSV")
    draw_arrow(ax, 25, 20, 28, 60, "GeoJSON")
    draw_arrow(ax, 38, 56, 38, 53, "")
    draw_arrow(ax, 48, 68, 51, 68, "UPSERT")
    draw_arrow(ax, 48, 38, 51, 55, "Data load")
    draw_arrow(ax, 62, 48, 62, 45, "JOIN")
    draw_arrow(ax, 51, 30, 48, 30, "Query")
    draw_arrow(ax, 48, 35, 76, 70, "JSON REST")
    draw_arrow(ax, 48, 32, 76, 44, "/riesgo-cruzado")
    draw_arrow(ax, 48, 28, 76, 18, "/historico")

    # Guardar en PNG y SVG
    p_png = os.path.join(OUTPUT_DIR, "figura_1_arquitectura_sistema.png")
    p_svg = os.path.join(OUTPUT_DIR, "figura_1_arquitectura_sistema.svg")
    plt.tight_layout()
    plt.savefig(p_png, dpi=300, bbox_inches="tight")
    plt.savefig(p_svg, bbox_inches="tight")
    plt.close()
    print(f"[OK] Guardada Figura 1: {p_png}")


# ==============================================================================
# FIGURA 2: DIAGRAMA DE FLUJO DETALLADO DEL PIPELINE ETL
# ==============================================================================
def generar_figura_2():
    print("-> Generando Figura 2: Diagrama de Flujo ETL...")
    fig, ax = setup_canvas(width=14, height=9, dpi=300)
    
    ax.text(50, 96.5, "FLUJO OPERATIVO DEL PIPELINE ETL DE ADQUISICIÓN Y ARMONIZACIÓN",
            ha="center", va="top", fontsize=13, fontweight="bold", color="#0F172A")
    ax.text(50, 93.5, "Secuencia de Ingesta, Filtrado de Atípicos, Normalización Espacial y Refresco de Riesgo",
            ha="center", va="top", fontsize=9.5, color="#475569")

    # 6 Etapas verticales
    etapas = [
        ("ETAPA 1: INGESTA TELEMÉTRICA CONTINUA",
         "Petición HTTP GET al feed KML de SIATA cada 2 minutos (scheduler.py / daemon).\nExtracción de etiquetas XML: <Placemark>, nombre de estación, coordenadas y <ICA_PM25_Valor>.",
         "#EFF6FF", "#3B82F6", "#1D4ED8", 78),
        ("ETAPA 2: DETECCIÓN DE ATÍPICOS Y CONTROL DE CALIDAD",
         "Filtrado de valores anómalos: PM2.5 < 0 o código -999 (mantenimiento/fuera de servicio) transformados a NULL.\nClasificación en categorías ICA según puntos de corte de la Resolución 2254 de 2017.",
         "#ECFDF5", "#10B981", "#047857", 63),
        ("ETAPA 3: ASIGNACIÓN TERRITORIAL Y RESOLUCIÓN GEOESPACIAL",
         "Paso A: Coincidencia textual directa mediante diccionario semántico MUNICIPIOS_MAPA.\nPaso B: Si falla, cálculo geodésico Haversine contra coordenadas de municipios oficiales (datos.gov.co).",
         "#FFFBEB", "#F59E0B", "#B45309", 48),
        ("ETAPA 4: CARGA RELACIONAL IDEMPOTENTE",
         "Inserción en tabla PostgreSQL mediciones_siata con cláusula ON CONFLICT (estacion, fecha_hora) DO NOTHING.\nPreservación de series temporales históricas sin duplicación de lecturas de sensores.",
         "#FAF5FF", "#A855F7", "#7E22CE", 33),
        ("ETAPA 5: FUSIÓN RELACIONAL Y REFRESCO DE VISTA MATERIALIZADA",
         "Ejecución de consulta CTE con DISTINCT ON (estacion) ORDER BY fecha_hora DESC para seleccionar el último dato.\nJOIN con catálogo de municipios, tabla de análisis de riesgo (β) y clasificador diagnóstico CIE-10.",
         "#F0FDF4", "#22C55E", "#15803D", 18),
        ("ETAPA 6: CÁLCULO DE INCREMENTO DE RIESGO RELATIVO (ΔR) Y PUBLICACIÓN API",
         "Evaluación de la función matemática: ΔR = (exp(β × PM2.5 / 10) - 1) × 100 por cada enfermedad.\nExposición inmediata en endpoints REST para consumo interactivo en el dashboard web AireSalud.",
         "#FFF7ED", "#F97316", "#C2410C", 3),
    ]

    for title, desc, bg, border, tcolor, y_pos in etapas:
        box = FancyBboxPatch((10, y_pos), 80, 11, boxstyle="round,pad=0.6,rounding_size=1.2",
                             edgecolor=border, facecolor=bg, linewidth=1.5)
        ax.add_patch(box)
        ax.text(12, y_pos + 8.8, title, ha="left", va="top", fontsize=9.5, fontweight="bold", color=tcolor)
        ax.text(12, y_pos + 6.0, desc, ha="left", va="top", fontsize=8, color="#1E293B", linespacing=1.35)

    # Flechas conectoras verticales
    for y_arrow in [78, 63, 48, 33, 18]:
        draw_arrow(ax, 50, y_arrow, 50, y_arrow - 4, lw=2.0, color="#475569")

    p_png = os.path.join(OUTPUT_DIR, "figura_2_diagrama_flujo_etl.png")
    p_svg = os.path.join(OUTPUT_DIR, "figura_2_diagrama_flujo_etl.svg")
    plt.tight_layout()
    plt.savefig(p_png, dpi=300, bbox_inches="tight")
    plt.savefig(p_svg, bbox_inches="tight")
    plt.close()
    print(f"[OK] Guardada Figura 2: {p_png}")


# ==============================================================================
# FIGURA 3: MODELO ENTIDAD-RELACIÓN (STAR SCHEMA)
# ==============================================================================
def generar_figura_3():
    print("-> Generando Figura 3: Modelo Entidad-Relación...")
    fig, ax = setup_canvas(width=16, height=9.5, dpi=300)
    
    ax.text(50, 97.2, "MODELO ENTIDAD-RELACIÓN EN ESTRELLA (STAR SCHEMA) EN POSTGRESQL",
            ha="center", va="top", fontsize=13, fontweight="bold", color="#0F172A")
    ax.text(50, 94.2, "Estructura de Datos para la Integración de Telemetría Ambiental y Epidemiología",
            ha="center", va="top", fontsize=9.5, color="#475569")

    # DIMENSIONES (Fila Superior)
    draw_box(ax, 5, 68, 26, 22, "municipios (Dimensión)", "Catálogo Territorial",
             ["PK  id: SERIAL",
              "    nombre: VARCHAR(100)",
              "    nombre_normalizado: VARCHAR UNIQUE"],
             bg="#EFF6FF", border="#3B82F6", title_color="#1D4ED8")

    draw_box(ax, 37, 68, 26, 22, "contaminantes (Dimensión)", "Parámetros Químicos",
             ["PK  id: SERIAL",
              "    nombre: VARCHAR(50) UNIQUE",
              "    nombre_display: VARCHAR(100)"],
             bg="#EFF6FF", border="#3B82F6", title_color="#1D4ED8")

    draw_box(ax, 69, 68, 26, 22, "grupos_diagnosticos (Dim)", "Clasificación CIE-10",
             ["PK  id: SERIAL",
              "    codigo_cie10: VARCHAR(50)",
              "    nombre: VARCHAR(255) UNIQUE",
              "    capitulo: VARCHAR(255)"],
             bg="#EFF6FF", border="#3B82F6", title_color="#1D4ED8")

    # HECHOS CENTRALES: analisis_riesgo & mediciones_siata
    draw_box(ax, 5, 27, 28, 35, "analisis_riesgo (Hechos)", "1.652 Registros de Coeficientes β",
             ["PK  id: SERIAL",
              "FK  municipio_id: INT → municipios.id",
              "FK  grupo_diagnostico_id: INT → grupos_diag.id",
              "FK  contaminante_id: INT → contaminantes.id",
              "    tipo_rezago: VARCHAR(50)",
              "    sexo: VARCHAR(50)",
              "    grupo_edad: VARCHAR(100)",
              "    beta: NUMERIC",
              "    exponencial_beta: NUMERIC",
              "    limite_inferior / superior: NUMERIC",
              "    porcentaje_incremento_riesgo: NUMERIC"],
             bg="#FEF3C7", border="#D97706", title_color="#B45309", title_fontsize=10)

    draw_box(ax, 37, 33, 26, 29, "mediciones_siata (Hechos)", "Telemetría en Tiempo Real",
             ["PK  id: SERIAL",
              "    estacion: VARCHAR(150)",
              "    pm25_ica: NUMERIC",
              "    fecha_hora: TIMESTAMP",
              "    latitud, longitud: NUMERIC",
              "    categoria_ica: VARCHAR(50)",
              "    fecha_carga: TIMESTAMP",
              "UK  (estacion, fecha_hora) [UPSERT]"],
             bg="#FEF3C7", border="#D97706", title_color="#B45309", title_fontsize=10)

    draw_box(ax, 67, 33, 28, 29, "enfermedades (Hechos)", "Morbilidad Histórica (2008–2017)",
             ["PK  id: SERIAL",
              "FK  municipio_id: INT → municipios.id",
              "FK  grupo_diagnostico_id: INT → grupos_diag.id",
              "    periodo: INT",
              "    sexo: VARCHAR(50)",
              "    grupo_edad: VARCHAR(100)",
              "    casos: INT"],
             bg="#FEF3C7", border="#D97706", title_color="#B45309", title_fontsize=10)

    # HECHOS ADICIONALES: defunciones & tasa_mortalidad
    draw_box(ax, 5, 3, 28, 20, "defunciones (Hechos)", "713 Registros de Mortalidad",
             ["PK  id: SERIAL",
              "FK  municipio_id: INT → municipios.id",
              "FK  grupo_diagnostico_id: INT → grupos_diag.id",
              "    periodo: INT, sexo, edad, muertes: NUMERIC"],
             bg="#FEF3C7", border="#D97706", title_color="#B45309", title_fontsize=9.5)

    draw_box(ax, 37, 3, 26, 20, "tasa_mortalidad (Hechos)", "600 Tasas Ajustadas",
             ["PK  id: SERIAL",
              "FK  municipio_id: INT → municipios.id",
              "    anio: INT, capitulo: VARCHAR",
              "    sexo: VARCHAR, tasa_ajustada: NUMERIC"],
             bg="#FEF3C7", border="#D97706", title_color="#B45309", title_fontsize=9.5)

    # VISTA INTEGRADA CONSOLIDADA
    draw_box(ax, 67, 3, 28, 25, "vista_riesgo_integrado (Vista)", "Cálculo Relacional ΔR en Vivo",
             ["• Cruza mediciones_siata + analisis_riesgo",
              "• SELECT DISTINCT ON (estacion) última lectura",
              "• JOIN ILIKE normalizado con municipios",
              "• Fórmula relacional:",
              "  ΔR = (exp(β · PM2.5/10) - 1) × 100",
              "• Genera: incremento_riesgo_pct_actual"],
             bg="#F3E8FF", border="#9333EA", title_color="#6B21A8", title_fontsize=9.5)

    # Relaciones y cardinalidades
    draw_arrow(ax, 18, 68, 18, 62, "1:N", color="#2563EB")
    draw_arrow(ax, 50, 68, 30, 62, "1:N", color="#2563EB")
    draw_arrow(ax, 82, 68, 33, 62, "1:N", color="#2563EB")
    draw_arrow(ax, 20, 68, 75, 62, "1:N", color="#2563EB")
    draw_arrow(ax, 82, 68, 80, 62, "1:N", color="#2563EB")
    draw_arrow(ax, 50, 33, 75, 28, "JOIN", color="#7C3AED")
    draw_arrow(ax, 33, 40, 67, 20, "JOIN", color="#7C3AED")

    p_png = os.path.join(OUTPUT_DIR, "figura_3_modelo_entidad_relacion.png")
    p_svg = os.path.join(OUTPUT_DIR, "figura_3_modelo_entidad_relacion.svg")
    plt.tight_layout()
    plt.savefig(p_png, dpi=300, bbox_inches="tight")
    plt.savefig(p_svg, bbox_inches="tight")
    plt.close()
    print(f"[OK] Guardada Figura 3: {p_png}")


# ==============================================================================
# FIGURA 7: FRAGMENTO DE CÓDIGO CLAVE (CÁLCULO DEL RR)
# ==============================================================================
def generar_figura_7():
    print("-> Generando Figura 7: Código de Cálculo de Riesgo...")
    fig, ax = setup_canvas(width=13, height=7.5, dpi=300)
    
    # Fondo estilo terminal oscuro
    card = FancyBboxPatch((4, 4), 92, 92, boxstyle="round,pad=1.0,rounding_size=1.8",
                          edgecolor="#334155", facecolor="#0F172A", linewidth=1.5)
    ax.add_patch(card)
    
    # Barra de ventana con botones macOS / IDE
    ax.add_patch(patches.Circle((7, 92.5), 0.9, facecolor="#EF4444", edgecolor="none"))
    ax.add_patch(patches.Circle((9.5, 92.5), 0.9, facecolor="#F59E0B", edgecolor="none"))
    ax.add_patch(patches.Circle((12, 92.5), 0.9, facecolor="#10B981", edgecolor="none"))
    
    ax.text(50, 92.5, "backend/app/routers/salud.py (Líneas 237–248) — Función Concentración-Respuesta",
            ha="center", va="center", fontsize=9.5, color="#94A3B8", family="monospace")
    ax.plot([4, 96], [90, 90], color="#1E293B", lw=1.2)

    codigo = [
        ("237", "# 7. Calcular incrementos de riesgo para cada enfermedad usando el PM2.5 real en vivo", "#64748B", True),
        ("238", "calculos = []", "#F8FAFC", False),
        ("239", "for f in filas_coef:", "#38BDF8", False),
        ("240", "    beta = float(f[\"beta\"])", "#F8FAFC", False),
        ("241", "    # Función concentración-respuesta estándar OMS / AirQ+:", "#10B981", True),
        ("242", "    # ΔR = (e^(β × PM2.5 / 10) - 1) × 100", "#10B981", True),
        ("243", "    inc_pct = round((math.exp(beta * (pm25_actual / 10.0)) - 1) * 100, 2)", "#FCD34D", False),
        ("244", "    calculos.append({", "#F8FAFC", False),
        ("245", "        \"enfermedad\": f[\"enfermedad\"],", "#F8FAFC", False),
        ("246", "        \"beta_historico\": beta,", "#F8FAFC", False),
        ("247", "        \"incremento_riesgo_porcentaje_actual\": inc_pct,", "#38BDF8", False),
        ("248", "        \"incremento_historico_base\": float(f[\"porcentaje_incremento_riesgo\"])", "#F8FAFC", False),
        ("249", "    })", "#F8FAFC", False),
        ("250", "# Ordenar de mayor a menor riesgo relativo atribuible", "#64748B", True),
        ("251", "calculos.sort(key=lambda x: x[\"incremento_riesgo_porcentaje_actual\"], reverse=True)", "#F8FAFC", False),
    ]

    curr_y = 85.5
    for num, linea, color, is_comment in codigo:
        # Número de línea
        ax.text(6.5, curr_y, num.rjust(3), ha="right", va="center", fontsize=8.5, color="#475569", family="monospace")
        # Separador vertical
        ax.text(8.0, curr_y, "│", ha="center", va="center", fontsize=8.5, color="#334155", family="monospace")
        # Línea de código
        fontstyle = "italic" if is_comment else "normal"
        fontweight = "bold" if num == "243" else "normal"
        ax.text(9.5, curr_y, linea, ha="left", va="center", fontsize=8.5, color=color, family="monospace",
                fontstyle=fontstyle, fontweight=fontweight)
        
        # Resaltado especial para la línea de la fórmula
        if num == "243":
            highlight = FancyBboxPatch((8.8, curr_y - 2.2), 85.5, 4.2, boxstyle="round,pad=0.2,rounding_size=0.5",
                                       edgecolor="#F59E0B", facecolor="#F59E0B", alpha=0.15, linewidth=1)
            ax.add_patch(highlight)
            
        curr_y -= 5.1

    p_png = os.path.join(OUTPUT_DIR, "figura_7_codigo_calculo_rr.png")
    p_svg = os.path.join(OUTPUT_DIR, "figura_7_codigo_calculo_rr.svg")
    plt.tight_layout()
    plt.savefig(p_png, dpi=300, bbox_inches="tight")
    plt.savefig(p_svg, bbox_inches="tight")
    plt.close()
    print(f"[OK] Guardada Figura 7: {p_png}")


if __name__ == "__main__":
    generar_figura_1()
    generar_figura_2()
    generar_figura_3()
    generar_figura_7()
    print("-> Generación de figuras completada con éxito.")

