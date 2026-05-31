import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de la Base de Datos PostgreSQL (Local o Nube)
# Si usas un servicio en la nube como Neon.tech, puedes pegar tu URL de conexión completa en DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", "")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")  # Cambiar por tu contraseña local
DB_NAME = os.getenv("DB_NAME", "calidad_aire_salud")


# Obtener ruta absoluta de la carpeta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUENTE_DATOS_DIR = os.path.join(BASE_DIR, "fuente_datos")

# Rutas a los Archivos CSV
CSV_ANALISIS_RIESGO = os.path.join(FUENTE_DATOS_DIR, "AnalisisRiesgo_20082017.csv")
CSV_ENFERMEDADES = os.path.join(FUENTE_DATOS_DIR, "EnfermedadesCalculadas_2008-2017.csv")
CSV_TASA_MORTALIDAD = os.path.join(FUENTE_DATOS_DIR, "TasaMortalidad_2008-2017.csv")
CSV_DEFUNCIONES = os.path.join(FUENTE_DATOS_DIR, "DefunsionesCalculadas_2008-2017.csv")

# Configuración API SIATA
# Se usa la URL KML oficial de SIATA para obtener mediciones de PM2.5 en tiempo real
SIATA_API_URL = "https://www.siata.gov.co/kml/01_Redes/AMVARedAire/RedAireAMVA_PM25.kml"


# Diccionario de Normalización de Municipios del Valle de Aburrá
# Mapea variantes encontradas en los CSV a un nombre normalizado estándar
MUNICIPIOS_MAPA = {
    'medellin': 'Medellín',
    'medellín': 'Medellín',
    'envigado': 'Envigado',
    'itagui': 'Itagüí',
    'itagüí': 'Itagüí',
    'sabaneta': 'Sabaneta',
    'bello': 'Bello',
    'caldas': 'Caldas',
    'copacabana': 'Copacabana',
    'la estrella': 'La Estrella',
    'laestrella': 'La Estrella',
    'girardota': 'Girardota',
    'barbosa': 'Barbosa'
}

# Diccionario de Normalización de Grupos de Edad
EDADES_MAPA = {
    'menores de 5 años': 'Menores de 5 años',
    'menor de 5 años': 'Menores de 5 años',
    'menores de 5': 'Menores de 5 años',
    '5 a 14 años': '5 a 14 años',
    '5 a 14': '5 a 14 años',
    '15 a 64 años': '15 a 64 años',
    '15 a 64': '15 a 64 años',
    '65 años y más': '65 años y más',
    '65 y más': '65 años y más',
    '65+': '65 años y más'
}