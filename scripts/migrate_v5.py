import sys
import os
import uuid

# Añadir path del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, Base, SessionLocal
from backend.models import Tienda, Usuario, Categoria, Producto, Cliente
from backend.utils.auth import get_password_hash

def run_migration():
    print("🚀 INICIANDO MIGRACIÓN ENTERPRISE V5.1 (RICH DATA SEEDING)...")
    
    # 1. Reset Total (Solo para desarrollo/industrialización)
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("✅ Base de datos reseteada y esquemas creados.")
    except Exception as e:
        print(f"❌ Error reseteando esquemas: {e}")
        return

    db = SessionLocal()
    try:
        # 2. Tienda Principal
        print("📦 Creando Entorno Multi-Tienda...")
        store = Tienda(
            id=str(uuid.uuid4()),
            nombre="Sede Central - Carbones y Pollos",
            direccion="Calle del Fuego, 12, Madrid",
            telefono="910000000"
        )
        db.add(store)
        db.commit()
        db.refresh(store)
        
        # 3. Administrador
        print("👤 Creando Staff Administrativo...")
        admin = Usuario(
            id=str(uuid.uuid4()),
            username="admin",
            full_name="CEO Admin Enterprise",
            pin_hash=get_password_hash("1234"),
            rol="ADMIN",
            tienda_id=store.id
        )
        db.add(admin)
        
        # 4. Categorías y Productos Gourmet
        print("🍽️ Poblando Catálogo de Productos...")
        cat_pollos = Categoria(id=str(uuid.uuid4()), nombre="Pollos al Carbón")
        cat_bebidas = Categoria(id=str(uuid.uuid4()), nombre="Bebidas y Refrescos")
        db.add_all([cat_pollos, cat_bebidas])
        db.commit()
        
        p1 = Producto(
            id=str(uuid.uuid4()),
            nombre="Pollo Entero Artesano",
            descripcion="Asado lentamente con carbón de encina",
            precio=14.50,
            impuesto=10.0,
            stock_actual=50.0,
            categoria_id=cat_pollos.id,
            tienda_id=store.id,
            imagen_url="https://images.unsplash.com/photo-1598103442097-8b74394b95c6?auto=format&fit=crop&w=400"
        )
        
        p2 = Producto(
            id=str(uuid.uuid4()),
            nombre="Medio Pollo + Patatas",
            descripcion="El clásico para comer solo",
            precio=8.90,
            impuesto=10.0,
            stock_actual=100.0,
            categoria_id=cat_pollos.id,
            tienda_id=store.id
        )
        
        p3 = Producto(
            id=str(uuid.uuid4()),
            nombre="Cerveza Especial 33cl",
            descripcion="Muy fría",
            precio=2.50,
            impuesto=21.0,
            stock_actual=200.0,
            categoria_id=cat_bebidas.id,
            tienda_id=store.id
        )
        
        db.add_all([p1, p2, p3])
        
        # 5. Clientes Fidelizados
        print("💎 Registrando Clientes VIP...")
        c1 = Cliente(
            id=str(uuid.uuid4()),
            nombre="Juan Cliente",
            telefono="600000001",
            puntos_fidelidad=150,
            nivel_fidelidad="PLATA",
            visitas=5
        )
        db.add(c1)
        
        db.commit()
        print("🎉 MIGRACIÓN Y SEEDING COMPLETADOS CON ÉXITO.")
        
    except Exception as e:
        print(f"❌ Error durante el seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_migration()
