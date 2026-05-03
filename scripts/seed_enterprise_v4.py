import sys
import os
import uuid

# Añadir el path del proyecto para importar los modelos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.database import SessionLocal, engine, Base
from backend.app.models.user import Usuario
from backend.app.models.product import Categoria, Producto
from backend.app.models.inventory import Ingrediente, RecetaItem
from backend.app.core.security import get_pin_hash

def seed():
    # Reset total del esquema para asegurar compatibilidad v4.0
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Limpiar datos previos para un seed limpio
        db.query(RecetaItem).delete()
        db.query(Producto).delete()
        db.query(Categoria).delete()
        db.query(Ingrediente).delete()
        db.query(Usuario).delete()
        
        # 2. Usuarios Admin y Staff
        admin = Usuario(
            id=str(uuid.uuid4()),
            username="admin",
            full_name="Administrador Enterprise",
            pin_hash=get_pin_hash("1234"),
            rol="ADMIN"
        )
        db.add(admin)

        # 3. Categorías
        cat_pollos = Categoria(id=str(uuid.uuid4()), nombre="Pollos al Carbón")
        cat_menus = Categoria(id=str(uuid.uuid4()), nombre="Menús Ahorro")
        cat_complementos = Categoria(id=str(uuid.uuid4()), nombre="Complementos")
        db.add_all([cat_pollos, cat_menus, cat_complementos])
        db.commit()

        # 4. Ingredientes (Costes)
        ing_pollo = Ingrediente(id=str(uuid.uuid4()), nombre="Pollo Crudo (1.2kg)", unidad_medida="unidad", coste_por_unidad=3.50)
        ing_carbon = Ingrediente(id=str(uuid.uuid4()), nombre="Carbón Vegetal", unidad_medida="kg", coste_por_unidad=0.80)
        ing_patatas = Ingrediente(id=str(uuid.uuid4()), nombre="Patatas", unidad_medida="kg", coste_por_unidad=0.60)
        ing_aceite = Ingrediente(id=str(uuid.uuid4()), nombre="Aceite Oliva", unidad_medida="l", coste_por_unidad=4.50)
        db.add_all([ing_pollo, ing_carbon, ing_patatas, ing_aceite])
        db.commit()

        # 5. Productos y Escandallos
        # Pollo Entero
        p_pollo = Producto(
            id=str(uuid.uuid4()), 
            nombre="Pollo Asado Entero", 
            precio=14.90, 
            categoria_id=cat_pollos.id
        )
        db.add(p_pollo)
        db.commit()
        
        # Receta Pollo Entero
        db.add(RecetaItem(producto_id=p_pollo.id, ingrediente_id=ing_pollo.id, cantidad_necesaria=1.0))
        db.add(RecetaItem(producto_id=p_pollo.id, ingrediente_id=ing_carbon.id, cantidad_necesaria=0.25))
        
        # Patatas Fritas
        p_patatas = Producto(
            id=str(uuid.uuid4()), 
            nombre="Patatas Fritas Grandes", 
            precio=4.50, 
            categoria_id=cat_complementos.id
        )
        db.add(p_patatas)
        db.commit()
        
        db.add(RecetaItem(producto_id=p_patatas.id, ingrediente_id=ing_patatas.id, cantidad_necesaria=0.5))
        db.add(RecetaItem(producto_id=p_patatas.id, ingrediente_id=ing_aceite.id, cantidad_necesaria=0.05))

        db.commit()
        
        # 6. Calcular costes iniciales
        from backend.app.services.financials import FinancialService
        FinancialService.update_all_product_costs(db)
        
        print("SUCCESS: SEED ENTERPRISE V4.0 COMPLETADO")
        
    except Exception as e:
        print(f"ERROR EN SEED: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
