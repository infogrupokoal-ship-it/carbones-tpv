import uuid
from backend.database import SessionLocal
from backend.models import Producto, Ingrediente, RecetaItem, Proveedor
from backend.utils.logger import logger

def seed_financial_intelligence():
    print("🚀 Iniciando Sembrado de Inteligencia Financiera (Escandallos)...")
    db = SessionLocal()
    
    try:
        # 1. Proveedores Estratégicos
        prov_data = [
            ("Suministros Avícolas del Valle", "info@avidelvalle.com", "Pollos y derivados"),
            ("Carboneras Unidas del Sur", "pedidos@carboneras.es", "Combustibles vegetales"),
            ("Huerta Gourmet", "ventas@huertagourmet.com", "Frutas y verduras")
        ]
        
        proveedores = {}
        for nombre, email, desc in prov_data:
            p = db.query(Proveedor).filter_by(nombre=nombre).first()
            if not p:
                p = Proveedor(id=str(uuid.uuid4()), nombre=nombre, contacto_email=email, descripcion=desc)
                db.add(p)
                db.commit()
            proveedores[nombre] = p

        # 2. Ingredientes con Coste Base
        ing_data = [
            ("Pollo Crudo (UD)", 4.50, "UD", "Suministros Avícolas del Valle"),
            ("Carbón de Encina (KG)", 1.20, "KG", "Carboneras Unidas del Sur"),
            ("Aceite de Oliva (L)", 8.50, "L", "Huerta Gourmet"),
            ("Patata Agria (KG)", 0.65, "KG", "Huerta Gourmet"),
            ("Mezcla Especias (KG)", 15.00, "KG", "Huerta Gourmet")
        ]
        
        ingredientes = {}
        for nombre, coste, unidad, prov_name in ing_data:
            ing = db.query(Ingrediente).filter_by(nombre=nombre).first()
            if not ing:
                ing = Ingrediente(
                    id=str(uuid.uuid4()),
                    nombre=nombre,
                    coste_unitario=coste,
                    unidad_medida=unidad,
                    proveedor_id=proveedores[prov_name].id,
                    stock_actual=500
                )
                db.add(ing)
                db.commit()
            ingredientes[nombre] = ing

        # 3. Recetas (Escandallos)
        # Pollo al Carbón de Encina
        pollo_prod = db.query(Producto).filter_by(nombre="Pollo al Carbón de Encina").first()
        if pollo_prod:
            # Limpiar receta vieja si existe para evitar duplicados en seed
            db.query(RecetaItem).filter_by(producto_id=pollo_prod.id).delete()
            
            items = [
                (ingredientes["Pollo Crudo (UD)"], 1.0),
                (ingredientes["Carbón de Encina (KG)"], 0.3),
                (ingredientes["Aceite de Oliva (L)"], 0.05),
                (ingredientes["Mezcla Especias (KG)"], 0.02)
            ]
            for ing, cant in items:
                db.add(RecetaItem(id=str(uuid.uuid4()), producto_id=pollo_prod.id, ingrediente_id=ing.id, cantidad_necesaria=cant))

        # Patatas Fritas
        patatas_prod = db.query(Producto).filter_by(nombre="Patatas Fritas 'Triple Cocción'").first()
        if patatas_prod:
            db.query(RecetaItem).filter_by(producto_id=patatas_prod.id).delete()
            items = [
                (ingredientes["Patata Agria (KG)"], 0.4),
                (ingredientes["Aceite de Oliva (L)"], 0.1)
            ]
            for ing, cant in items:
                db.add(RecetaItem(id=str(uuid.uuid4()), producto_id=patatas_prod.id, ingrediente_id=ing.id, cantidad_necesaria=cant))

        db.commit()
        print("✅ Escandallos y Recetas vinculadas correctamente.")
        print("🚀 [SUCCESS] Financial Intelligence Seeder Completado.")

    except Exception as e:
        db.rollback()
        print(f"❌ [ERROR] Sembrado financiero fallido: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_financial_intelligence()
