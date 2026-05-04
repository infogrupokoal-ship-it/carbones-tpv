import sys
import os
import uuid
import logging

# Ensure backend modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import SessionLocal, engine
from backend.models import Base, Usuario
from backend.utils.auth import get_password_hash

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("UpdateAdmin")

def update_or_create_admin(username: str, new_pin: str):
    if len(new_pin) < 4:
        logger.error("El PIN debe tener al menos 4 caracteres.")
        return

    if new_pin == "1234":
        logger.error("El PIN no puede ser 1234 por razones de seguridad.")
        return

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        user = db.query(Usuario).filter(Usuario.username == username).first()
        if user:
            logger.info(f"Usuario '{username}' encontrado. Actualizando PIN...")
            user.pin_hash = get_password_hash(new_pin)
            logger.info("PIN actualizado correctamente.")
        else:
            logger.info(f"Usuario '{username}' no encontrado. Creando nuevo admin...")
            new_admin = Usuario(
                id=str(uuid.uuid4()),
                username=username,
                pin_hash=get_password_hash(new_pin),
                rol="ADMIN",
                is_active=True
            )
            db.add(new_admin)
            logger.info(f"Usuario administrador '{username}' creado exitosamente.")
        
        db.commit()
        logger.info("✅ Operación completada con éxito. Ya puedes iniciar sesión.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error al actualizar admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python scripts/update_admin.py <usuario> <nuevo_pin>")
        print("Ejemplo: python scripts/update_admin.py admin 9999")
        sys.exit(1)
    
    username_arg = sys.argv[1]
    pin_arg = sys.argv[2]
    update_or_create_admin(username_arg, pin_arg)
