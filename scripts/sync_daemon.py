import time
import sqlite3
import os
import logging
from datetime import datetime

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sync_daemon.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SyncDaemon")

DB_PATH = os.environ.get("DATABASE_PATH", "tpv_data.sqlite")
CLOUD_ENDPOINT = os.environ.get("CLOUD_SYNC_ENDPOINT", "https://tpv-cloud.example.com/api/sync")
API_KEY = os.environ.get("SYNC_API_KEY", "offline_edge_key")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def sync_pedidos_pendientes():
    """
    Busca pedidos en la BD local que no estén marcados como sincronizados
    y los envía al cloud. (Implementación de stub para el plan Edge-to-Cloud).
    """
    logger.info("Iniciando ciclo de sincronización...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # En un modelo real, habría una columna 'synced' o 'cloud_id'
        # Para la Fase 2, validamos que la BD exista y simulemos el health check
        cursor.execute("SELECT count(*) as count FROM pedidos WHERE estado = 'ESPERANDO_PAGO'")
        row = cursor.fetchone()
        logger.info(f"Pedidos esperando pago localmente: {row['count']}")
        
        # Ejemplo de payload a enviar al cloud
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "edge_id": "NODE_01",
            "pending_count": row['count']
        }
        
        # Simulación de POST
        # response = requests.post(CLOUD_ENDPOINT, json=payload, headers={"Authorization": f"Bearer {API_KEY}"})
        # if response.status_code == 200:
        #     logger.info("Sincronización exitosa con la nube.")
        # else:
        #     logger.warning(f"Error sincronizando: {response.status_code}")
            
        logger.info("Ciclo de sincronización completado (Simulado Offline-First).")
        
    except Exception as e:
        logger.error(f"Error en el Sync Daemon: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    logger.info("Iniciando TPV Sync Daemon (Offline-First Edge Node)...")
    while True:
        sync_pedidos_pendientes()
        # Dormir 60 segundos antes de la próxima sincronización
        time.sleep(60)
