import os, sys
from dotenv import load_dotenv

env_path = r'c:\Users\ASUS\Documents\mariana\itm_mariana\Integracion y adquisición de datos\proyecto\monitoreo_calidad_aire_para_salud\backend\.env'
load_dotenv(env_path)
sys.path.append(r'c:\Users\ASUS\Documents\mariana\itm_mariana\Integracion y adquisición de datos\proyecto\monitoreo_calidad_aire_para_salud\backend')

from app.database import get_db

with get_db() as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'vista_riesgo_integrado';
        """)
        cols = cur.fetchall()
        print('Columns in vista_riesgo_integrado:')
        for c in cols:
            print(' ', c['column_name'], ':', c['data_type'])

        # Also get view definition
        cur.execute("""
            SELECT definition 
            FROM pg_views 
            WHERE viewname = 'vista_riesgo_integrado';
        """)
        view_def = cur.fetchone()
        if view_def:
            print('\nView definition:')
            print(view_def['definition'])

