import os, sys
from dotenv import load_dotenv

env_path = r'c:\Users\ASUS\Documents\mariana\itm_mariana\Integracion y adquisición de datos\proyecto\monitoreo_calidad_aire_para_salud\backend\.env'
load_dotenv(env_path)
sys.path.append(r'c:\Users\ASUS\Documents\mariana\itm_mariana\Integracion y adquisición de datos\proyecto\monitoreo_calidad_aire_para_salud\backend')

from app.database import get_connection
from etl.carga.vista_integrada import crear_vista_datos_integrados

conn = get_connection()
try:
    print("Creando vista materializada...")
    crear_vista_datos_integrados(conn)
    print("Vista materializada actualizada exitosamente.")
finally:
    conn.close()

