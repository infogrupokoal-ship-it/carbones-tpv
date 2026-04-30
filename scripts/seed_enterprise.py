from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal, engine, Base
from backend.app.models.user import Usuario
from backend.app.models.product import Categoria, Producto
from backend.app.core import security

def seed_enterprise():
    print("🚀 Iniciando Seed Data Enterprise v4.0...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Crear Usuario Admin
        admin = db.query(Usuario).filter(Usuario.username == "admin").first()
        if not admin:
            admin = Usuario(
                username="admin",
                email="admin@carbonesypollos.com",
                rol="ADMIN",
                pin_hash=security.get_pin_hash("1234"), # PIN por defecto
                is_active=True
            )
            db.add(admin)
            print("✅ Usuario 'admin' creado (PIN: 1234)")
        
        # 2. Crear Categorías Base
        if not db.query(Categoria).first():
            cat_pollos = Categoria(nombre="Pollos Asados", orden=1)
            cat_bebidas = Categoria(nombre="Bebidas", orden=2)
            db.add_all([cat_pollos, cat_bebidas])
            db.flush()
            
            # 3. Crear Productos Base
            p1 = Producto(
                nombre="Pollo Entero",
                precio=12.50,
                categoria_id=cat_pollos.id,
                stock_actual=50
            )
            db.add(p1)
            print("✅ Categorías y productos base inyectados.")
            
        db.commit()
        print("⭐ Sistema Enterprise inicializado correctamente.")
        
    except Exception as e:
        print(f"❌ Error en seed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_enterprise()
