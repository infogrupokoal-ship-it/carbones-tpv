import logging
import os
import time
import signal
import sys
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Cargar configuraciÃ³n desde .env
load_dotenv()

# ConfiguraciÃ³n Profesional
VPS_URL = os.environ.get("VPS_URL", "https://carbones-tpv.onrender.com")
LOCAL_DB_PATH = os.environ.get("DATABASE_URL", "sqlite:///./tpv_data.sqlite")
SYNC_INTERVAL = int(os.environ.get("SYNC_INTERVAL", 15))

# Logging con rotaciÃ³n y formato profesional
INSTANCE_DIR = "instance"
if not os.path.exists(INSTANCE_DIR):
    os.makedirs(INSTANCE_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [SYNC_DAEMON] %(message)s",
    handlers=[logging.FileHandler(os.path.join(INSTANCE_DIR, "sync.log")), logging.StreamHandler()]
)
logger = logging.getLogger("SyncDaemon")

# Bloqueo de PID para evitar mÃºltiples instancias
PID_FILE = os.path.join(INSTANCE_DIR, "sync_daemon.pid")

def acquire_lock():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                old_pid = int(f.read().strip())
            # Verificar si el proceso sigue vivo (Unix/Windows compatible)
            if os.name == 'posix':
                os.kill(old_pid, 0)
            else:
                import ctypes
                PROCESS_QUERY_INFORMATION = 0x0400
                handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, old_pid)
                if handle != 0:
                    ctypes.windll.kernel32.CloseHandle(handle)
                else:
                    raise OSError
                    
            logger.error(f"âŒ Ya hay una instancia ejecutÃ¡ndose (PID: {old_pid}). Abortando.")
            sys.exit(1)
        except (OSError, ValueError):
            os.remove(PID_FILE)

    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

def release_lock():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

engine = create_engine(LOCAL_DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

running = True

def handle_exit(signum, frame):
    global running
    logger.info("Recibida seÃ±al de parada. Finalizando sincronizaciÃ³n de forma segura...")
    running = False
    release_lock()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

def push_local_data():
    """EnvÃ­a pedidos locales nuevos al servidor central."""
    db = SessionLocal()
    try:
        from backend.models import Pedido
        pedidos_unsynced = db.query(Pedido).filter(Pedido.is_synced.is_(False)).all()


        
        if not pedidos_unsynced:
            return

        payload = []
        for p in pedidos_unsynced:
            payload.append({
                "id": p.id,
                "numero_ticket": p.numero_ticket,
                "total": p.total,
                "estado": p.estado,
                "fecha": p.fecha.isoformat() if p.fecha else None,
                "items": [{"nombre": it.nombre, "cantidad": it.cantidad, "precio": it.precio} for it in p.items] if hasattr(p, 'items') else []
            })

        response = requests.post(f"{VPS_URL}/api/sync/push", json={"pedidos": payload}, timeout=15)
        if response.status_code == 200:
            for p in pedidos_unsynced:
                p.is_synced = True
            db.commit()
            logger.info(f"âœ… Sincronizados {len(pedidos_unsynced)} pedidos con Ã©xito.")
    except Exception as e:
        logger.error(f"âŒ Error en PUSH: {str(e)}")
    finally:
        db.close()

def pull_remote_data():
    """Descarga actualizaciones desde la nube (Pedidos de WhatsApp, etc)."""
    db = SessionLocal()
    try:
        from backend.models import Pedido
        response = requests.get(f"{VPS_URL}/api/sync/pull", timeout=15)
        if response.status_code == 200:
            data = response.json()
            nuevos = data.get("nuevos_pedidos", [])
            for p_dict in nuevos:
                existe = db.query(Pedido).filter_by(id=p_dict.get('id')).first()
                if existe:
                    continue
                    
                logger.info(f"ðŸ“¥ Nuevo pedido remoto recibido: {p_dict['numero_ticket']}")
                
                p_local = Pedido(
                    id=p_dict.get('id'),
                    numero_ticket=p_dict['numero_ticket'],
                    total=p_dict['total'],
                    origen="WHATSAPP",
                    is_synced=True,
                    estado="PENDIENTE"
                )
                db.add(p_local)
                db.commit()
    except Exception as e:
        logger.debug(f"Servidor remoto no disponible para PULL: {str(e)}")
    finally:
        db.close()

def daemon_loop():
    acquire_lock()
    logger.info(f"ðŸš€ Demonio de SincronizaciÃ³n v4.5 Industrializado (Target: {VPS_URL})")
    
    while running:
        start_time = time.time()
        try:
            push_local_data()
            pull_remote_data()
            # La gestiÃ³n de hardware se delega al local_printer_bridge.py por limpieza arquitectÃ³nica
        except Exception as e:
            logger.error(f"Fallo crÃ­tico en el loop: {e}")
        
        # Ajustar el sleep para mantener el intervalo exacto
        elapsed = time.time() - start_time
        sleep_time = max(0, SYNC_INTERVAL - elapsed)
        time.sleep(sleep_time)
    
    release_lock()
    logger.info("ðŸ‘‹ Sync Daemon detenido correctamente.")

if __name__ == "__main__":
    daemon_loop()
