"""
Asignación de municipios a estaciones SIATA mediante datos oficiales.

Este módulo implementa una estrategia de respaldo para la asignación de municipio cuando la
coincidencia por nombre (ILIKE) falla. Utiliza el dataset oficial de municipios del
Departamento (https://www.datos.gov.co/resource/gdxc-w37w.json) que contiene latitud y
longitud de cada municipio.

Uso típico:
    df_siata = extraer_siata()
    df_siata = asignar_municipio(df_siata)

Se descarga el dataset una única vez y se almacena en caché bajo
`backend/etl/data/municipios_oficiales.json`.
"""

import os
import json
import math
import requests
import pandas as pd

from etl.configuracion.settings import BASE_DIR
from etl.configuracion.diccionarios import MUNICIPIOS_MAPA

# Ruta de caché del dataset oficial de municipios
DATASET_URL = "https://www.datos.gov.co/resource/gdxc-w37w.json"
CACHE_DIR = os.path.join(BASE_DIR, "etl", "data")
CACHE_FILE = os.path.join(CACHE_DIR, "municipios_oficiales.json")


def _descargar_dataset():
    """Descarga el dataset oficial de municipios y lo guarda en caché.
    Si el archivo ya existe, se reutiliza para evitar llamadas repetidas.
    Returns:
        pd.DataFrame con columnas: municipio, latitud, longitud.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    if not os.path.isfile(CACHE_FILE):
        print("[INFO] Descargando dataset oficial de municipios…")
        resp = requests.get(DATASET_URL, timeout=20)
        resp.raise_for_status()
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            f.write(resp.text)
    # Cargar JSON en DataFrame
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    df = pd.json_normalize(raw)
    df["municipio"] = df["municipio"].str.strip().str.upper()
    df["latitud"] = pd.to_numeric(df["latitud"], errors="coerce")
    df["longitud"] = pd.to_numeric(df["longitud"], errors="coerce")
    return df[["municipio", "latitud", "longitud"]]


def _haversine(lat1, lon1, lat2, lon2):
    """Calcula la distancia (km) entre dos puntos geográficos usando Haversine."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def asignar_municipio(df_siata: pd.DataFrame) -> pd.DataFrame:
    """Asigna el municipio a cada estación de SIATA.

    1. Intenta la coincidencia por nombre usando ``MUNICIPIOS_MAPA``.
    2. Si falla, usa la distancia geodésica hacia el municipio más cercano
       del dataset oficial.
    """
    municipios_oficiales = _descargar_dataset()

    def _resolver(row):
        nombre = row.get("estacion") or ""
        nombre_norm = nombre.upper().strip()
        municipio = MUNICIPIOS_MAPA.get(nombre_norm)
        if municipio:
            return municipio.upper()
        lat, lon = row.get("latitud"), row.get("longitud")
        if pd.isna(lat) or pd.isna(lon):
            return None
        distances = municipios_oficiales.apply(
            lambda m: _haversine(lat, lon, m["latitud"], m["longitud"]), axis=1
        )
        idx_min = distances.idxmin()
        return municipios_oficiales.at[idx_min, "municipio"]

    df_siata["municipio_normalizado"] = df_siata.apply(_resolver, axis=1)
    return df_siata
