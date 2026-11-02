"""
Daemon de Extracción Periódica — Scheduler SIATA
===================================================
Automatiza la extracción de datos de la API SIATA para mantener
las mediciones de PM2.5 actualizadas en la base de datos.

Modos de operación
-------------------
    Producción:    python -m etl.scheduler        → cada 1 hora
    Demostración:  python -m etl.scheduler --demo  → cada 10 segundos

    El modo demo es ideal para mostrar en la sustentación cómo
    la base de datos se puebla en tiempo real ante el evaluador.

Relación con la metodología
---------------------------
    Este módulo implementa la AUTOMATIZACIÓN del pipeline:
    - Ejecuta la extracción de SIATA de forma recurrente
    - Usa la estrategia UPSERT para evitar duplicados
    - Garantiza la CONTINUIDAD del flujo de información
"""

import sys
import os
import time
import argparse
from datetime import datetime

# Asegurar que backend/ esté en el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import schedule

from etl.extraccion.siata_api import extraer_siata
from etl.carga.conexion import get_connection, crear_base_de_datos_si_no_existe
from etl.carga.esquema import crear_esquema
from etl.carga.siata import cargar_mediciones_siata


def job_extraccion_siata():
    """
    Tarea periódica: extrae datos actuales de SIATA e inserta en PostgreSQL.
    Diseñada para ser invocada por el scheduler de forma recurrente.
    """
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{ahora}] [INFO] Iniciando ciclo automático de actualización de SIATA...")

    try:
        # Extraer datos en tiempo real
        df_siata = extraer_siata()

        # Conectar y guardar de forma idempotente (UPSERT)
        conn = get_connection()
        cargar_mediciones_siata(conn, df_siata)
        conn.close()

        print(f"[{ahora}] [OK] Ciclo completado. Esperando próxima ejecución...")
    except Exception as e:
        print(f"[ERROR] Error durante la extracción automática de SIATA: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Daemon de Extracción Periódica para API SIATA."
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Inicia en modo demostración (ejecuta cada 10 segundos).",
    )
    args = parser.parse_args()

    print("=" * 80)
    print("         DAEMON DE EXTRACCIÓN PERIÓDICA: CALIDAD DEL AIRE")
    print("=" * 80)

    # Verificar conexión inicial y crear esquema si no existe
    try:
        crear_base_de_datos_si_no_existe()
        crear_esquema()
    except Exception as e:
        print(f"[ERROR] Error de conexión a PostgreSQL: {e}")
        print("Asegúrate de que PostgreSQL esté activo antes de iniciar el scheduler.")
        sys.exit(1)

    # Configurar frecuencia según el modo
    if args.demo:
        intervalo_segundos = 10
        print("[DEMO] MODO DEMOSTRACIÓN ACTIVO")
        print(f"-> Extrayendo datos de SIATA cada {intervalo_segundos} segundos.")
        schedule.every(intervalo_segundos).seconds.do(job_extraccion_siata)
    else:
        print("[PROD] MODO PRODUCCIÓN")
        print("-> Extrayendo datos de SIATA cada 1 hora.")
        schedule.every(1).hours.do(job_extraccion_siata)

    # Ejecutar una vez al arrancar
    print("\n[INICIO] Ejecutando extracción inicial de arranque...")
    job_extraccion_siata()

    print("\nPress Ctrl+C to stop the scheduler daemon.")
    print("-" * 80)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[FIN] Scheduler detenido por el usuario. Saliendo...")


# ─────────────────────────────────────────────────────────────────────────────
# Punto de entrada: python -m etl.scheduler [--demo]
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
