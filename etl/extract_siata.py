import requests
from xml.etree import ElementTree as ET
import re
import pandas as pd
from datetime import datetime
import urllib3

try:
    from config import SIATA_API_URL
except ImportError:
    from etl.config import SIATA_API_URL

# Desactivar advertencias de SSL no verificado (para verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_pm25_siata():
    """
    Se conecta al API KML de SIATA que funciona correctamente,
    extrae las mediciones de PM2.5 y las formatea en un DataFrame de Pandas para PostgreSQL.
    """
    url = SIATA_API_URL
    print(f"-> Extrayendo datos de calidad del aire desde SIATA (KML): {url}")

    
    try:
        # Petición HTTP igual a api_sia_actual.py (con verify=False para evitar problemas de SSL local)
        r = requests.get(url, timeout=15, verify=False)
        r.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Error al conectar con SIATA API: {e}")
        return pd.DataFrame()

    # Limpiar xmlns namespaces para búsquedas directas
    content = re.sub(b'xmlns="[^"]+"', b'', r.content)
    
    try:
        kml = ET.fromstring(content)
    except Exception as e:
        print(f"[ERROR] Error al parsear XML/KML de SIATA: {e}")
        return pd.DataFrame()


    estaciones = []
    for placemark in kml.findall('.//Placemark'):
        nombre = placemark.findtext('name', '').strip()
        val = None
        fecha = "Sin fecha"
        
        extended_data = placemark.find('.//SchemaData')
        if extended_data is not None:
            for simple_data in extended_data.findall('SimpleData'):
                nombre_campo = simple_data.get('name')
                
                # Buscamos el valor de PM2.5 (ICA)
                if nombre_campo == 'ICA_PM25_Valor':
                    try:
                        val = float(simple_data.text)
                        if val < 0:
                            val = None
                    except:
                        val = None
                
                elif nombre_campo == 'fecha_ultima_actualizacion':
                    fecha = simple_data.text
        
        # Coordenadas
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
            'estacion': nombre,
            'pm25_ica': val,
            'fecha_hora': fecha,
            'latitud': lat,
            'longitud': lon,
            'categoria_ica': obtener_categoria_ica(val),
            'fecha_carga': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
    df = pd.DataFrame(estaciones)
    
    # Estandarizar fecha de carga y fecha_hora
    if not df.empty:
        df.loc[df['fecha_hora'] == 'Sin fecha', 'fecha_hora'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    print(f"[OK] SIATA (KML): Extracción exitosa. {len(df)} estaciones procesadas.")
    return df

def obtener_categoria_ica(pm25):
    """
    Categorización del Índice de Calidad del Aire (ICA)
    """
    if pm25 is None or pd.isna(pm25): 
        return 'Sin dato'
    if pm25 < 12:    
        return 'Buena'
    if pm25 < 35:    
        return 'Moderada'
    if pm25 < 55:    
        return 'Dañina para grupos sensibles'
    if pm25 < 150:   
        return 'Dañina'
    if pm25 < 250:   
        return 'Muy dañina'
    return 'Peligrosa'

if __name__ == '__main__':
    df = get_pm25_siata()
    if not df.empty:
        print(df.head(5))
