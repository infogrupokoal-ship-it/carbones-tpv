import logging
from .database import SessionLocal
from .models import Producto, Usuario
from scripts.seed_ultra import seed_ultra_industrial
from .utils.auth import get_password_hash
import uuid

logger = logging.getLogger("seeding")

def run_auto_seeding():
    """
    Motor de persistencia inteligente: Verifica la integridad del catálogo
    y ejecuta un sembrado automático si se detecta un entorno vacío.
    Garantiza que el sistema siempre inicie con datos profesionales en Render.
    """
    db = SessionLocal()
    try:
        producto_count = db.query(Producto).count()
        if producto_count == 0:
            logger.info("📭 Base de datos vacía detectada. Iniciando sembrado Ultra-Premium...")
            seed_ultra_industrial()
            
            # Asegurar usuario admin por defecto
            if not db.query(Usuario).filter_by(username="admin").first():
                admin = Usuario(
                    id=str(uuid.uuid4()), 
                    username="admin", 
                    pin_hash=get_password_hash("1234"), 
                    rol="admin"
                )
                db.add(admin)
                db.commit()
                logger.info("👤 Usuario 'admin' creado (PIN: 1234).")
            
            logger.info("✅ Sembrado automático completado con éxito.")
        else:
            logger.info(f"📊 El sistema ya contiene {producto_count} productos. Saltando auto-seeding.")
    except Exception as e:
        logger.error(f"❌ Fallo crítico en el proceso de auto-seeding: {e}")
        db.rollback()
    finally:
        db.close()
