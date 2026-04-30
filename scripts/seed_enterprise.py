from sqlalchemy.orm import Session
import sys
import os

# Ajuste de path para que encuentre el paquete 'backend'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, engine, Base
from backend.models import Usuario, Categoria, Producto, Cliente, Proveedor, Ingrediente
from backend.utils.logger import logger

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
                pin="1234"
            )
            db.add(admin)
            print("✅ Usuario 'admin' creado (PIN: 1234)")
        
        # 2. Crear Categorías Base
        if not db.query(Categoria).first():
            cat_pollos = Categoria(nombre="Pollos Asados", orden=1)
            cat_bebidas = Categoria(nombre="Bebidas", orden=2)
            cat_pizzas = Categoria(nombre="Pizzas", orden=3)
            db.add_all([cat_pollos, cat_bebidas, cat_pizzas])
            db.flush()
            
            # 3. Crear Productos Base
            p1 = Producto(
                nombre="Pollo Entero",
                precio=12.50,
                categoria_id=cat_pollos.id,
                stock_actual=50,
                stock_minimo=10
            )
            db.add(p1)
            db.flush()
            
            p2 = Producto(
                nombre="Medio Pollo",
                precio=7.50,
                categoria_id=cat_pollos.id,
                stock_actual=100,
                stock_base_id=p1.id,
                factor_stock=0.5
            )
            p3 = Producto(
                nombre="Coca Cola 33cl",
                precio=2.00,
                categoria_id=cat_bebidas.id,
                stock_actual=240,
                stock_minimo=24
            )
            p4 = Producto(
                nombre="Pizza Barbacoa",
                precio=11.90,
                categoria_id=cat_pizzas.id,
                stock_actual=20
            )
            db.add_all([p2, p3, p4])
            
            # 4. Proveedores e Ingredientes
            prov = Proveedor(nombre="Avícola del Sur", telefono="600000001", email="pedidos@avicola.com")
            db.add(prov)
            db.flush()
            
            ing = Ingrediente(nombre="Pollo Crudo", unidad_medida="UD", stock_actual=60, stock_minimo=15, proveedor_id=prov.id)
            db.add(ing)
            
            print("✅ Categorías, productos, proveedores e ingredientes inyectados.")
            
        db.commit()
        print("⭐ Sistema Enterprise inicializado correctamente.")
        
    except Exception as e:
        print(f"❌ Error en seed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_enterprise()
