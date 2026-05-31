import schedule
import time
import sys
import argparse
from datetime import datetime

# Asegurar importación de carpetas locales
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extract_siata import get_pm25_siata
import db_postgres

def job_extraccion_siata():
    """
    Tarea periódica ejecutada por el scheduler para obtener
    los datos más recientes de calidad del aire e insertarlos.
    """
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{ahora}] [INFO] Iniciando ciclo automático de actualización de SIATA...")
    
    try:
        # Extraer datos en tiempo real
        df_siata = get_pm25_siata()
        
        # Conectar y guardar de forma idempotente (UPSERT)
        conn = db_postgres.get_connection()
        db_postgres.cargar_mediciones_siata(conn, df_siata)
        conn.close()
        
        print(f"[{ahora}] [OK] Ciclo completado. Esperando proxima ejecucion...")
    except Exception as e:
        print(f"[ERROR] Error durante la extraccion automatica de SIATA: {e}")

def main():
    parser = argparse.ArgumentParser(description="Daemon de Extraccion Periodica para API SIATA.")
    parser.add_argument(
        "--demo", 
        action="store_true", 
        help="Inicia el programador en modo demostracion (ejecuta cada 10 segundos)."
    )
    args = parser.parse_args()

    print("=" * 80)
    print("             DAEMON DE EXTRACCION PERIODICA: CALIDAD DEL AIRE")
    print("=" * 80)
    
    # Probar conexión inicial y crear tabla si no existe
    try:
        db_postgres.crear_base_de_datos_si_no_existe()
        db_postgres.crear_esquema()
    except Exception as e:
        print(f"[ERROR] Error de conexion a PostgreSQL: {e}")
        print("Asegurate de que PostgreSQL este activo antes de iniciar el scheduler.")
        sys.exit(1)

    # Configurar frecuencia según el modo
    if args.demo:
        intervalo_segundos = 10
        print("[DEMO] MODO DEMOSTRACION ACTIVO")
        print(f"-> Extrayendo datos de SIATA cada {intervalo_segundos} segundos.")
        schedule.every(intervalo_segundos).seconds.do(job_extraccion_siata)
    else:
        print("[PROD] MODO PRODUCCION SIMULADO")
        print("-> Extrayendo datos de SIATA cada 1 hora.")
        schedule.every(1).hours.do(job_extraccion_siata)

    # Ejecutar una vez al arrancar
    print("\n[INICIO] Ejecutando extraccion inicial de arranque...")
    job_extraccion_siata()

    print("\nPress Ctrl+C to stop the scheduler daemon.")
    print("-" * 80)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[FIN] Scheduler detenido por el usuario. Saliendo...")


if __name__ == "__main__":
    main()
