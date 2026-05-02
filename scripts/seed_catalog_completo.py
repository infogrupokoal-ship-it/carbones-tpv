"""
seed_catalog_completo.py - Catálogo completo del negocio real
Ejecutar en Render via force_seed o localmente para poblar la BD
"""
import uuid, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, engine
from backend.models import Categoria, Producto, Tienda, Usuario
from backend.utils.auth import get_password_hash

CATALOG = {
    # ── POLLOS ──────────────────────────────────────────────────────────────
    "Pollos Asados 🔥": [
        {"nombre": "Pollo Entero al Carbón",         "precio": 10.90, "desc": "Pollo de primera calidad asado en brasa de carbón de encina. Nuestro superventas.", "img": "https://images.unsplash.com/photo-1598103442097-8b74394b95c6?w=800&q=80"},
        {"nombre": "Medio Pollo al Carbón",           "precio":  5.90, "desc": "Media unidad del pollo estrella, ideal para 1 persona.", "img": "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=800&q=80"},
        {"nombre": "Cuarto de Pollo",                 "precio":  3.50, "desc": "Un cuarto de pollo, perfecto para acompañar o para los más pequeños."},
        {"nombre": "Alitas al Carbón (1kg)",          "precio":  8.50, "desc": "Kilogramo de alitas marinadas y asadas a la brasa. Para compartir."},
        {"nombre": "Muslos de Pollo (4uds)",          "precio":  7.90, "desc": "4 muslos de pollo cocinados a fuego lento sobre carbón de encina."},
        {"nombre": "Pechuga a la Brasa",              "precio":  6.50, "desc": "Pechuga entera a la brasa, jugosa y tierna. Baja en grasa."},
    ],
    # ── BOCADILLOS ───────────────────────────────────────────────────────────
    "Bocadillos & Baguettes 🥖": [
        {"nombre": "Bocadillo de Pollo a la Brasa",   "precio":  4.50, "desc": "Tierno pollo a la brasa con tomate, lechuga y nuestra salsa especial en pan de chapata."},
        {"nombre": "Bocadillo de Serranito",           "precio":  5.50, "desc": "Lomo, jamón serrano, pimiento frito y tomate. Un clásico andaluz."},
        {"nombre": "Bocadillo de Chicharrones",        "precio":  4.00, "desc": "Chicharrones de cerdo crujientes en pan de telera."},
        {"nombre": "Baguette de Pollo y Queso",        "precio":  5.00, "desc": "Pollo a la brasa con queso fundido y salsa de miel mostaza."},
        {"nombre": "Bocadillo de Jamón Ibérico",       "precio":  5.90, "desc": "Jamón ibérico de bellota en pan artesano."},
        {"nombre": "Bocadillo Vegetal",                "precio":  4.50, "desc": "Pimientos asados, queso fresco, rúcula y vinagreta en pan integral."},
    ],
    # ── HAMBURGUESAS ─────────────────────────────────────────────────────────
    "Hamburguesas 🍔": [
        {"nombre": "Burger Koal Classic",              "precio": 10.90, "desc": "200g de ternera, queso cheddar, lechuga, tomate, cebolla y salsa secreta.", "img": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800&q=80"},
        {"nombre": "Burger Doble Koal",                "precio": 13.90, "desc": "400g de carne, doble queso y todo lo demás. Para los valientes."},
        {"nombre": "Burger de Pollo Crujiente",        "precio":  9.90, "desc": "Filetes de pechuga rebozados crujientes con salsa sriracha y col."},
        {"nombre": "Burger Veggie",                    "precio":  9.50, "desc": "Hamburguesa de garbanzos y verduras asadas, con aguacate y sprouts."},
        {"nombre": "Burger Koal BBQ",                  "precio": 11.90, "desc": "Ternera con salsa BBQ ahumada, bacon crujiente y cebolla caramelizada."},
    ],
    # ── PIZZAS ───────────────────────────────────────────────────────────────
    "Pizzas Artesanas 🍕": [
        {"nombre": "Pizza Margarita",                  "precio":  9.50, "desc": "Tomate, mozzarella y albahaca fresca. Simple y perfecta.", "img": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=800&q=80"},
        {"nombre": "Pizza Pollo y Champiñones",        "precio": 12.50, "desc": "Pollo a la brasa, champiñones frescos, queso mozzarella y orégano."},
        {"nombre": "Pizza Cuatro Quesos",              "precio": 12.00, "desc": "Mozzarella, gorgonzola, emmental y parmesano. Para los amantes del queso."},
        {"nombre": "Pizza Pepperoni",                  "precio": 11.50, "desc": "Pepperoni americano con extra de mozzarella."},
        {"nombre": "Pizza BBQ Pollo",                  "precio": 13.00, "desc": "Salsa BBQ, pollo a la brasa, cebolla roja y mozzarella."},
        {"nombre": "Pizza Vegetal",                    "precio": 11.00, "desc": "Pimientos, berenjena, tomate cherry, aceitunas y queso de cabra."},
    ],
    # ── ARROCES ──────────────────────────────────────────────────────────────
    "Arroces & Paellas 🥘": [
        {"nombre": "Arroz con Pollo",                  "precio":  9.00, "desc": "Arroz cremoso cocinado en el jugo de nuestros pollos. Tradición pura.", "img": "https://images.unsplash.com/photo-1589502011-5bef0c2b5c5a?w=800&q=80"},
        {"nombre": "Paella Valenciana (2 personas)",   "precio": 22.00, "desc": "Paella tradicional con pollo, conejo, garrofón y verduras de temporada."},
        {"nombre": "Arroz al Horno",                   "precio": 11.00, "desc": "Arroz al horno tradicional con costillas y embutido."},
        {"nombre": "Arroz Negro con Alioli",           "precio": 13.00, "desc": "Arroz negro con tinta de calamar y alioli casero."},
    ],
    # ── SANDWICHES ───────────────────────────────────────────────────────────
    "Sándwiches & Snacks 🥪": [
        {"nombre": "Sándwich Mixto",                   "precio":  3.50, "desc": "Jamón york y queso fundido en pan de molde tostado."},
        {"nombre": "Sándwich Club",                    "precio":  5.50, "desc": "Pollo, bacon, queso, lechuga, tomate y mahonesa. Tres pisos."},
        {"nombre": "Wrap de Pollo",                    "precio":  6.00, "desc": "Tortilla de trigo con pollo, guacamole, maíz y lechuga."},
        {"nombre": "Nuggets de Pollo (8uds)",          "precio":  5.00, "desc": "8 nuggets de pollo crujientes con salsa a elegir."},
        {"nombre": "Croquetas de Pollo (6uds)",        "precio":  5.50, "desc": "Croquetas caseras de pollo asado con bechamel artesanal."},
    ],
    # ── COMPLEMENTOS ─────────────────────────────────────────────────────────
    "Complementos 🍟": [
        {"nombre": "Patatas Fritas (Ración)",           "precio":  3.50, "desc": "Patatas caseras fritas en aceite de girasol. Crujientes por fuera, tiernas por dentro.", "img": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=800&q=80"},
        {"nombre": "Patatas Fritas (Tapa)",             "precio":  1.90, "desc": "Tapa de patatas fritas para acompañar."},
        {"nombre": "Ensalada Mixta",                   "precio":  4.50, "desc": "Lechuga, tomate, cebolla, maíz, zanahoria y aceituna con vinagreta."},
        {"nombre": "Ensalada César",                   "precio":  6.00, "desc": "Romana, pollo a la brasa, parmesano, crutones y salsa César."},
        {"nombre": "Pimientos Asados",                 "precio":  4.50, "desc": "Pimientos rojos asados al carbón con aceite de oliva virgen extra."},
        {"nombre": "Pan con Tomate y Aceite",          "precio":  2.00, "desc": "Pan artesano con tomate triturado y aceite de oliva virgen."},
        {"nombre": "Guarnición Parrilla (Verduras)",   "precio":  5.50, "desc": "Selección de verduras de temporada asadas en la brasa."},
    ],
    # ── BEBIDAS ──────────────────────────────────────────────────────────────
    "Bebidas 🥤": [
        {"nombre": "Coca-Cola 33cl",                   "precio":  2.20, "desc": "Refresco clásico."},
        {"nombre": "Fanta Naranja 33cl",               "precio":  2.20, "desc": "Refresco de naranja."},
        {"nombre": "Fanta Limón 33cl",                 "precio":  2.20, "desc": "Refresco de limón."},
        {"nombre": "Agua Mineral 50cl",                "precio":  1.50, "desc": "Agua mineral natural."},
        {"nombre": "Agua con Gas 50cl",                "precio":  1.80, "desc": "Agua mineral con gas."},
        {"nombre": "Zumo de Naranja Natural",          "precio":  2.50, "desc": "Zumo de naranja recién exprimido."},
        {"nombre": "Nestea 33cl",                      "precio":  2.20, "desc": "Té helado de limón."},
        {"nombre": "Cerveza Mahou 33cl",               "precio":  2.50, "desc": "Cerveza nacional en lata."},
        {"nombre": "Cerveza Sin Alcohol 33cl",         "precio":  2.30, "desc": "Cerveza 0.0%."},
        {"nombre": "Coca-Cola 2L",                     "precio":  4.50, "desc": "Botella 2 litros, ideal para llevar."},
    ],
    # ── COMBOS ───────────────────────────────────────────────────────────────
    "Combos Ahorro 🛍️": [
        {"nombre": "Menú Personal",                    "precio":  9.90, "desc": "1/2 Pollo + Patatas + Refresco. El menú del día de toda la vida.", "img": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80"},
        {"nombre": "Menú Familiar",                    "precio": 28.90, "desc": "2 Pollos enteros + 2 Patatas grandes + 4 Refrescos. Para toda la familia."},
        {"nombre": "Combo Pareja",                     "precio": 18.90, "desc": "1 Pollo + Patatas medianas + 2 Refrescos. Cena romántica en casa."},
        {"nombre": "Pack Party (4 personas)",          "precio": 39.90, "desc": "2 Pollos + 4 Hamburguesas + Patatas XL + 4 Refrescos. Para la fiesta."},
        {"nombre": "Menú Infantil",                    "precio":  7.90, "desc": "1/4 Pollo + Patatas pequeñas + Zumo. Para los peques de la casa."},
        {"nombre": "Combo Pechuga Fit",                "precio": 11.50, "desc": "Pechuga + Ensalada Mixta + Agua. Para cuidarse sin perder sabor."},
        {"nombre": "Pack Alitas (Fiesta)",             "precio": 22.00, "desc": "2kg de alitas + 4 Patatas + 4 Refrescos. ¡Al tapeo!"},
    ],
    # ── POSTRES ──────────────────────────────────────────────────────────────
    "Postres Caseros 🍰": [
        {"nombre": "Tarta de Queso",                   "precio":  3.50, "desc": "Tarta de queso cremosa al estilo vasco, hecha en casa."},
        {"nombre": "Flan de Huevo",                    "precio":  2.50, "desc": "Flan casero con caramelo tostado."},
        {"nombre": "Helado (2 bolas)",                 "precio":  2.50, "desc": "Dos bolas de helado artesano a elegir entre los sabores del día."},
        {"nombre": "Brownie con Helado",               "precio":  4.50, "desc": "Brownie de chocolate caliente con bola de vainilla y coulis de frutos rojos."},
        {"nombre": "Fruta de Temporada",               "precio":  2.00, "desc": "Selección de fruta fresca de temporada."},
    ],
}

def seed_completo():
    from backend.utils.logger import logger
    db = SessionLocal()
    try:
        # Tienda
        tienda = db.query(Tienda).filter_by(nombre="Carbones y Pollos La Granja").first()
        if not tienda:
            tienda = db.query(Tienda).first()
        if not tienda:
            tienda = Tienda(id=str(uuid.uuid4()), nombre="Carbones y Pollos La Granja",
                            direccion="Av. Malvarrosa 112, 46011 Valencia", telefono="963 000 000")
            db.add(tienda)
            db.commit()

        total_creados = 0
        total_actualizados = 0

        for cat_nombre, productos in CATALOG.items():
            # Crear/obtener categoría
            cat = db.query(Categoria).filter_by(nombre=cat_nombre).first()
            if not cat:
                cat = Categoria(id=str(uuid.uuid4()), nombre=cat_nombre)
                db.add(cat)
                db.commit()

            for p_data in productos:
                existing = db.query(Producto).filter_by(nombre=p_data["nombre"]).first()
                if existing:
                    # Actualizar precio si ha cambiado
                    if existing.precio != p_data["precio"]:
                        existing.precio = p_data["precio"]
                        total_actualizados += 1
                    if not existing.imagen_url and p_data.get("img"):
                        existing.imagen_url = p_data.get("img")
                    existing.is_active = True
                else:
                    p = Producto(
                        id=str(uuid.uuid4()),
                        nombre=p_data["nombre"],
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
        print(f"[OK] Seed completo: {total_creados} creados, {total_actualizados} actualizados")
        print(f"[OK] Total categorías: {len(CATALOG)}")
        print(f"[OK] Total productos: {sum(len(v) for v in CATALOG.values())}")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] {e}")
        import traceback; traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_completo()
