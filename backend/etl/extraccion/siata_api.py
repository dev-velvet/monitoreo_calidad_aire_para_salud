"""
Extracción de Datos de la API SIATA (Fuente Primaria — Sensor)
================================================================
Este módulo se conecta al feed KML público del Sistema de Alerta Temprana
del Valle de Aburrá (SIATA) para extraer las mediciones de PM2.5 en
tiempo real de las estaciones de monitoreo de calidad del aire.

Relación con la metodología
---------------------------
Corresponde a la Fase 1 (Identificación de fuentes - dimensión ambiental):
    - Protocolo: peticiones HTTP GET al feed KML de SIATA
    - Formato: XML/KML con campos SchemaData por estación
    - Frecuencia de actualización del sensor: cada 2 minutos
    - Variables extraídas: PM2.5 (µg/m³), coordenadas geográficas, fecha

Detección de atípicos (respuesta a evaluadores)
-------------------------------------------------
    - Valores -999 (Representan ausencia de datos por datos invalidos, datos faltantes
        o periodos anteriores o posteriores a la instalación de un equipo en una estación determinada 
        https://siata.gov.co/Informes_Aire/131_InformeOperacion_Agosto2025/F-GAA-SIATA-RA-75_Informe_operacion_agosto2025_V2.pdf).
        → se convierten a NULL
    - Valores PM2.5 < 0 → se convierten a NULL
    - Estaciones sin coordenadas → se conservan con lat/lon = NULL

Función de agregación temporal (respuesta a evaluadores)
---------------------------------------------------------
    NO se usa promedio, suma ni mediana sobre las lecturas de alta frecuencia.
    Se selecciona la MEDICIÓN MÁS RECIENTE por estación usando:
        DISTINCT ON (estacion) ORDER BY fecha_hora DESC
    Esto garantiza que el sistema refleje el estado ambiental instantáneo.
"""

import re
import pandas as pd
import requests
import urllib3
from xml.etree import ElementTree as ET
from datetime import datetime

from etl.configuracion.settings import SIATA_API_URL

# Desactivar advertencias de SSL no verificado (para verify=False en redes locales)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def extraer_siata():
    """
    Extrae las mediciones actuales de PM2.5 de la API SIATA.

    Proceso:
        1. Petición HTTP GET al feed KML de SIATA
        2. Limpieza de namespaces XML para facilitar el parseo
        3. Iteración sobre cada <Placemark> (= estación de monitoreo)
        4. Extracción de: nombre, PM2.5, fecha, coordenadas
        5. Filtro de valores atípicos: -999 y negativos → NULL
        6. Clasificación ICA según Resolución 2254 de 2017 (Colombia)

    Returns:
        pd.DataFrame con columnas:
            estacion, pm25_ica, fecha_hora, latitud, longitud,
            categoria_ica, fecha_carga
    """
    print(f"-> Extrayendo datos de calidad del aire desde SIATA (KML): {SIATA_API_URL}")

    # ── Paso 1: Petición HTTP GET ──────────────────────────────────────────
    try:
        respuesta = requests.get(SIATA_API_URL, timeout=15, verify=False)
        respuesta.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Error al conectar con SIATA API: {e}")
        return pd.DataFrame()

    # ── Paso 2: Limpiar namespaces XML ─────────────────────────────────────
    contenido = re.sub(b'xmlns="[^"]+"', b'', respuesta.content)

    try:
        kml = ET.fromstring(contenido)
    except Exception as e:
        print(f"[ERROR] Error al parsear XML/KML de SIATA: {e}")
        return pd.DataFrame()

    # ── Paso 3-5: Extraer datos por estación ───────────────────────────────
    estaciones = []
    for placemark in kml.findall('.//Placemark'):
        nombre = placemark.findtext('name', '').strip()
        valor_pm25 = None
        fecha = "Sin fecha"

        # Buscar campos en SchemaData
        extended_data = placemark.find('.//SchemaData')
        if extended_data is not None:
            for simple_data in extended_data.findall('SimpleData'):
                nombre_campo = simple_data.get('name')

                # Extraer valor de PM2.5 (ICA)
                if nombre_campo == 'ICA_PM25_Valor':
                    try:
                        valor_pm25 = float(simple_data.text)
                        # DETECCIÓN DE ATÍPICOS: -999 = mantenimiento, <0 = error
                        if valor_pm25 < 0:
                            valor_pm25 = None
                    except (ValueError, TypeError):
                        valor_pm25 = None

                elif nombre_campo == 'fecha_ultima_actualizacion':
                    fecha = simple_data.text

        # Extraer coordenadas geográficas del KML
        coords = placemark.findtext('.//coordinates', '')
        lon, lat = None, None
        if coords:
            partes = coords.strip().split(',')
            if len(partes) >= 2:
                try:
                    lon, lat = float(partes[0]), float(partes[1])
                except ValueError:
                    pass

        estaciones.append({
            'estacion':      nombre,
            'pm25_ica':      valor_pm25,
            'fecha_hora':    fecha,
            'latitud':       lat,
            'longitud':      lon,
            'categoria_ica': _clasificar_ica(valor_pm25),
            'fecha_carga':   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

    # ── Paso 6: Construir DataFrame ────────────────────────────────────────
    df = pd.DataFrame(estaciones)

    if not df.empty:
        # Reemplazar fechas faltantes con timestamp actual
        sin_fecha = df['fecha_hora'] == 'Sin fecha'
        df.loc[sin_fecha, 'fecha_hora'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"[OK] SIATA (KML): Extracción exitosa. {len(df)} estaciones procesadas.")
    return df


def _clasificar_ica(pm25):
    """
    Clasifica el valor de PM2.5 en categorías del Índice de Calidad del Aire (ICA)
    según los puntos de corte de la Resolución 2254 de 2017 (Colombia), Tabla No. 6.

    Los puntos de corte corresponden a promedios de 24 horas; aquí se aplican a la
    lectura instantánea de SIATA como aproximación operativa.

    Umbrales (µg/m³):
        0-12    → Buena
        13-37   → Aceptable
        38-55   → Dañina a la salud de grupos sensibles
        56-150  → Dañina para la salud
        151-250 → Muy dañina para la salud
        251-500 → Peligrosa
        >500    → Peligrosa (fuera de la escala ICA)
    """
    if pm25 is None or pd.isna(pm25):
        return 'Sin dato'
    if pm25 <= 12:
        return 'Buena'
    if pm25 <= 37:
        return 'Aceptable'
    if pm25 <= 55:
        return 'Dañina a la salud de grupos sensibles'
    if pm25 <= 150:
        return 'Dañina para la salud'
    if pm25 <= 250:
        return 'Muy dañina para la salud'
    return 'Peligrosa'


# ─────────────────────────────────────────────────────────────────────────────
# Ejecución directa para pruebas
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    df = extraer_siata()
    if not df.empty:
        print(df.head(5))
