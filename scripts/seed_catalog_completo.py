"""
seed_catalog_completo.py - Catálogo completo del negocio real
Ejecutar en Render via force_seed o localmente para poblar la BD
"""
import uuid
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, engine, Base
from backend.models import Categoria, Producto, Tienda, Usuario

print(f"DEBUG: Engine URL: {engine.url}")
Base.metadata.create_all(bind=engine)

CATALOG = {
    "Pollos": [
        {"nombre": "Pollo Entero al Carbón", "precio": 10.90, "desc": "Pollo asado en brasa de carbón de encina.", "img": "/static/img/pollo_asado.png"},
        {"nombre": "Medio Pollo al Carbón", "precio": 5.90, "desc": "Media unidad del pollo estrella.", "img": "/static/img/pollo_asado.png"},
        {"nombre": "Cuarto de Pollo", "precio": 3.50, "desc": "Un cuarto de pollo."},
        {"nombre": "Alitas al Carbón (1kg)", "precio": 8.50, "desc": "Kilogramo de alitas."},
    ],
    "Arroces": [
        {"nombre": "Arroz con Pollo", "precio": 9.00, "desc": "Arroz cremoso con jugo de pollo.", "img": "/static/img/pollo_asado.png"},
        {"nombre": "Paella Valenciana", "precio": 22.00, "desc": "Paella tradicional."},
    ],
    "Bocadillos": [
        {"nombre": "Bocadillo de Pollo", "precio": 4.50, "desc": "Tierno pollo a la brasa."},
        {"nombre": "Bocadillo de Serranito", "precio": 5.50, "desc": "Lomo, jamón serrano, pimiento y tomate."},
    ],
    "Hamburguesas": [
        {"nombre": "Burger Carbones Classic", "precio": 10.90, "desc": "200g de ternera, queso cheddar.", "img": "/static/img/pollo_asado.png"},
        {"nombre": "Burger Doble", "precio": 13.90, "desc": "400g de carne, doble queso."},
    ],
    "Pizzas": [
        {"nombre": "Pizza Margarita", "precio": 9.50, "desc": "Tomate, mozzarella y albahaca fresca.", "img": "/static/img/pollo_asado.png"},
        {"nombre": "Pizza Pollo y Champiñones", "precio": 12.50, "desc": "Pollo a la brasa y champiñones."},
    ],
    "Quijadas": [
        {"nombre": "Quijada al Carbón", "precio": 14.50, "desc": "Quijada de cerdo asada a fuego lento."},
    ],
    "Codillos": [
        {"nombre": "Codillo Asado", "precio": 12.00, "desc": "Codillo asado tradicional."},
    ],
    "Raciones": [
        {"nombre": "Ración de Patatas", "precio": 3.50, "desc": "Patatas caseras fritas.", "img": "/static/img/pollo_asado.png"},
        {"nombre": "Croquetas de Pollo (6uds)", "precio": 5.50, "desc": "Croquetas caseras."},
        {"nombre": "Nuggets de Pollo (8uds)", "precio": 5.00, "desc": "Nuggets crujientes."},
    ],
    "Ensaladas": [
        {"nombre": "Ensalada Mixta", "precio": 4.50, "desc": "Lechuga, tomate, cebolla, maíz."},
        {"nombre": "Ensalada César", "precio": 6.00, "desc": "Romana, pollo a la brasa, parmesano."},
    ],
    "Bebidas": [
        {"nombre": "Coca-Cola 33cl", "precio": 2.20, "desc": "Refresco clásico."},
        {"nombre": "Agua Mineral 50cl", "precio": 1.50, "desc": "Agua mineral natural."},
        {"nombre": "Cerveza Mahou 33cl", "precio": 2.50, "desc": "Cerveza nacional en lata."},
    ],
    "Salsas": [
        {"nombre": "Salsa Alioli", "precio": 1.00, "desc": "Salsa alioli casera."},
        {"nombre": "Salsa Brava", "precio": 1.00, "desc": "Salsa brava."},
    ],
    "Menús": [
        {"nombre": "Menú Personal", "precio": 9.90, "desc": "1/2 Pollo + Patatas + Refresco.", "img": "/static/img/pollo_asado.png"},
        {"nombre": "Menú Familiar", "precio": 28.90, "desc": "2 Pollos + 2 Patatas + 4 Refrescos."},
    ],
    "Promos": [
        {"nombre": "Promo Pareja", "precio": 18.90, "desc": "1 Pollo + Patatas + 2 Refrescos."},
        {"nombre": "Pack Party", "precio": 39.90, "desc": "2 Pollos + 4 Burgers + Patatas + 4 Refrescos."},
    ],
}

def seed_completo():
    db = SessionLocal()
    try:
        # Tienda
        tienda = db.query(Tienda).filter_by(nombre="Carbones y Pollos La Granja").first()
        if not tienda:
            tienda = db.query(Tienda).first()
        if not tienda:
            tienda = Tienda(
                id=str(uuid.uuid4()), 
                nombre="Carbones y Pollos La Granja",
                direccion="Av. Malvarrosa 112, 46011 Valencia", 
                telefono="963 000 000"
            )
            db.add(tienda)
            db.commit()

        # Usuario Admin (PIN 1234 restringido a entornos locales/demo)
        from backend.utils.auth import get_password_hash
        from backend.config import settings
        
        is_demo_or_local = settings.DEBUG or os.getenv("ENVIRONMENT") == "local" or os.getenv("DEMO_MODE") == "true"
        
        if not db.query(Usuario).filter_by(username="admin").first():
            if is_demo_or_local:
                admin = Usuario(
                    id=str(uuid.uuid4()),
                    username="admin",
                    full_name="Gerente Carbones (DEMO)",
                    pin_hash=get_password_hash("1234"),
                    rol="ADMIN",
                    tienda_id=tienda.id
                )
                db.add(admin)
                db.commit()
                print("[OK] Usuario ADMIN de prueba creado (PIN: 1234)")
            else:
                print("[WARN] Saltando creación de usuario 'admin/1234' por seguridad (Entorno Producción).")

        total_creados = 0
        total_actualizados = 0

        # LIMPIEZA ZERO-TOUCH DE PRODUCTOS ANTIGUOS CON "KOAL"
        try:
            koal_prods = db.query(Producto).filter(Producto.nombre.like('%Koal%')).all()
            for kp in koal_prods:
                kp.nombre = kp.nombre.replace('Koal', 'Carbones')
                kp.is_active = True
                db.add(kp)
            db.commit()
            if koal_prods:
                print(f"[OK] Saneados {len(koal_prods)} productos legacy de Koal.")
        except Exception as e:
            print(f"[WARN] No se pudo limpiar productos legacy: {e}")

        # MIGRACIÓN DE NOMBRES DE CATEGORÍAS LEGACY A LIMPIOS
        rename_map = {
            "Pollos Asados 🔥": "Pollos",
            "Bocadillos & Baguettes 🥖": "Bocadillos",
            "Hamburguesas 🍔": "Hamburguesas",
            "Hamburguesas Pro 🍔": "Hamburguesas",
            "Pizzas Artesanas 🍕": "Pizzas",
            "Arroces & Paellas 🥘": "Arroces",
            "Sándwiches & Snacks 🥪": "Sándwiches",
            "Complementos 🍟": "Raciones",
            "Bebidas 🥤": "Bebidas",
            "Bebidas Frías 🥤": "Bebidas",
            "Combos Ahorro 🛍️": "Promos",
            "Postres Caseros 🍰": "Postres",
            "Salsas 🧄": "Salsas",
            "Menús 🍱": "Menús",
        }
        for old_name, new_name in rename_map.items():
            cat = db.query(Categoria).filter_by(nombre=old_name).first()
            if cat:
                cat.nombre = new_name
                db.add(cat)
        db.commit()

        for cat_nombre, productos in CATALOG.items():
            # Crear/obtener categoría
            cat = db.query(Categoria).filter_by(nombre=cat_nombre).first()
            if not cat:
                cat = Categoria(id=str(uuid.uuid4()), nombre=cat_nombre)
                db.add(cat)
                db.commit()

            for p_data in productos:
                # Normalizar nombres para evitar duplicados por Koal
                p_nombre = p_data["nombre"].replace("Koal", "Carbones")
                existing = db.query(Producto).filter_by(nombre=p_nombre).first()
                if existing:
                    # Actualizar precio si ha cambiado
                    if existing.precio != p_data["precio"]:
                        existing.precio = p_data["precio"]
                        total_actualizados += 1
                    if not existing.imagen_url and p_data.get("img"):
                        existing.imagen_url = p_data.get("img")
                    existing.is_active = True
                    existing.categoria_id = cat.id
                else:
                    p = Producto(
                        id=str(uuid.uuid4()),
                        nombre=p_nombre,
                        descripcion=p_data["desc"],
                        precio=p_data["precio"],
                        categoria_id=cat.id,
                        tienda_id=tienda.id,
                        stock_actual=100,
                        imagen_url=p_data.get("img"),
                        alergenos=p_data.get("alergenos", "Ver alérgenos en mostrador"),
                        is_active=True
                    )
                    db.add(p)
                    total_creados += 1

        db.commit()
        
        # DESACTIVAR CATEGORÍAS QUE NO ESTÁN EN EL CATÁLOGO OFICIAL
        valid_cat_names = set(CATALOG.keys())
        all_cats = db.query(Categoria).all()
        for c in all_cats:
            if c.nombre not in valid_cat_names:
                if hasattr(c, 'is_active'):
                    c.is_active = False
                db.add(c)
        db.commit()

        print(f"[OK] Seed completo: {total_creados} creados, {total_actualizados} actualizados")
        print(f"[OK] Total categorías: {len(CATALOG)}")
        print(f"[OK] Total productos: {sum(len(v) for v in CATALOG.values())}")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    seed_completo()
