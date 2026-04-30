import sys
import os
import uuid

# Añadir path del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, Base, SessionLocal
from backend.models import Tienda, Usuario
from backend.utils.auth import get_password_hash  # Corregido name

def run_migration():
    print("🚀 INICIANDO MIGRACIÓN ENTERPRISE V5.0 (RUTAS CORREGIDAS)...")
    
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Esquemas de base de datos creados/verificados.")
    except Exception as e:
        print(f"❌ Error creando esquemas: {e}")
        return

    db = SessionLocal()
    try:
        store = db.query(Tienda).first()
        if not store:
            print("📦 Creando Tienda Principal (Sede Central)...")
            store = Tienda(
                id=str(uuid.uuid4()),
                nombre="Sede Central - Carbones y Pollos",
                direccion="Calle del Fuego, 12, Madrid",
                telefono="910000000"
            )
            db.add(store)
            db.commit()
            db.refresh(store)
        
        admin = db.query(Usuario).filter(Usuario.username == "admin").first()
        if not admin:
            print("👤 Creando Administrador Global...")
            admin = Usuario(
                id=str(uuid.uuid4()),
                username="admin",
                full_name="CEO Admin Enterprise",
                pin_hash=get_password_hash("1234"),
                rol="ADMIN",
                tienda_id=store.id
            )
            db.add(admin)
            db.commit()
        
        print("🎉 MIGRACIÓN COMPLETADA CON ÉXITO.")
        
    except Exception as e:
        print(f"❌ Error durante la migración de datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_migration()
