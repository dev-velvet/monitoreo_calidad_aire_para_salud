import os, sys
from dotenv import load_dotenv

env_path = r'c:\Users\ASUS\Documents\mariana\itm_mariana\Integracion y adquisición de datos\proyecto\monitoreo_calidad_aire_para_salud\backend\.env'
load_dotenv(env_path)
sys.path.append(r'c:\Users\ASUS\Documents\mariana\itm_mariana\Integracion y adquisición de datos\proyecto\monitoreo_calidad_aire_para_salud\backend')

from app.database import get_db

with get_db() as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT attname
            FROM pg_attribute
            WHERE attrelid = 'vista_riesgo_integrado'::regclass
              AND attnum > 0
              AND NOT attisdropped;
        """)
        cols = [r['attname'] for r in cur.fetchall()]
        print("Actual columns in vista_riesgo_integrado:", cols)

