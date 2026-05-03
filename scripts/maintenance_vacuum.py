import sqlite3
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("maintenance.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MaintenanceDB")

DB_PATH = os.environ.get("DATABASE_PATH", "tpv_data.sqlite")

def run_vacuum():
    """
    Ejecuta el comando VACUUM en SQLite para recuperar espacio y optimizar el rendimiento.
    Debe ejecutarse en horarios de baja carga (ej. 4:00 AM).
    """
    logger.info("Iniciando rutina de mantenimiento: VACUUM")
    
    if not os.path.exists(DB_PATH):
        logger.warning(f"La base de datos {DB_PATH} no existe. Saltando VACUUM.")
        return

    try:
        # Mostramos tamaño previo
        size_before = os.path.getsize(DB_PATH) / (1024 * 1024)
        logger.info(f"Tamaño de BD antes de VACUUM: {size_before:.2f} MB")
        
        conn = sqlite3.connect(DB_PATH)
        # SQLite recomienda asegurar que no haya transacciones pendientes
        conn.isolation_level = None
        conn.execute("VACUUM")
        conn.close()
        
        # Mostramos tamaño posterior
        size_after = os.path.getsize(DB_PATH) / (1024 * 1024)
        logger.info(f"Tamaño de BD después de VACUUM: {size_after:.2f} MB")
        logger.info(f"Espacio recuperado: {(size_before - size_after):.2f} MB")
        logger.info("Mantenimiento VACUUM completado con éxito.")
        
    except Exception as e:
        logger.error(f"Error durante el mantenimiento VACUUM: {e}")

if __name__ == "__main__":
    logger.info("Script de Mantenimiento Automático (Zero-Touch)")
    # En un entorno real se usaría cron, pero para el edge node puede correr bloqueando o usar un scheduler como `schedule`
    # Por ahora simplemente lo ejecutamos
    run_vacuum()
