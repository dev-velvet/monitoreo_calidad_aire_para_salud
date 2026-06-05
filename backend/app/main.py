import sys
import os
import threading
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Asegurar importación de subdirectorios
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.routers import municipios, siata, salud

app = FastAPI(
    title="API de Monitoreo de Calidad del Aire y Salud Pública",
    description="Backend en FastAPI para el Dashboard de Calidad del Aire y Morbilidad en el Valle de Aburrá.",
    version="1.0.0"
)

# Configuración de CORS para conectar con Lovable
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local Vite / Lovable sandbox
        "http://localhost:3000",
        "https://*.lovable.app",  # Wildcard para dominios de Lovable
        "https://lovable.app",
        "https://airwise-health.onrender.com", # Frontend desplegado en Render
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(municipios.router)
app.include_router(siata.router)
app.include_router(salud.router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "proyecto": "Monitoreo de Calidad del Aire para Salud Pública - Valle de Aburrá",
        "docs_url": "/docs"
    }

# ----------------------------------------------------------------------------
# Hilo de Fondo (Background Thread) para el Scheduler de SIATA
# ----------------------------------------------------------------------------
def run_siata_scheduler():
    """
    Función que ejecuta el scheduler de SIATA de fondo para mantener 
    las mediciones en tiempo real actualizadas cada 1 hora.
    """
    print("[SCHEDULER] Iniciando hilo de fondo para actualizar SIATA...")
    # Importar scheduler localmente para evitar circular imports
    try:
        from etl.scheduler import job_extraccion_siata
        import schedule
        
        # Ejecutar una vez al arrancar
        job_extraccion_siata()
        
        # Programar cada hora
        schedule.every(1).hours.do(job_extraccion_siata)
        
        while True:
            schedule.run_pending()
            time.sleep(10)
    except Exception as e:
        print(f"[SCHEDULER ERROR] Falló el hilo de fondo de SIATA: {e}")

# Iniciar el scheduler en un hilo separado cuando arranque la app
scheduler_thread = threading.Thread(target=run_siata_scheduler, daemon=True)
scheduler_thread.start()
