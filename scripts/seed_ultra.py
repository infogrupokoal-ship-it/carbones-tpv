import uuid
import sys
from backend.database import SessionLocal, Base, engine
from backend.models import Categoria, Producto, Usuario, Tienda, Ingrediente, Proveedor
from backend.utils.auth import get_password_hash
from backend.utils.logger import logger

def seed_ultra_industrial():
    logger.info("Iniciando Sembrado MEGA INDUSTRIAL v2.1...")
    db = SessionLocal()
    
    try:
        # 0. Limpiar datos previos para asegurar frescura (Opcional, pero recomendado para "vacio" fix)
        # db.query(Producto).delete()
        # db.query(Categoria).delete()
        # db.commit()

        # 1. Crear Tienda Central
        tienda = db.query(Tienda).filter_by(nombre="Carbones y Pollos Central").first()
        if not tienda:
            tienda = Tienda(
                id=str(uuid.uuid4()),
                nombre="Carbones y Pollos Central",
                direccion="Av. del Fuego, 123",
                telefono="900-KOAL-TPV"
            )
            db.add(tienda)
            db.commit()
            logger.info(f"Tienda Central Creada: {tienda.id}")

        # 2. Usuarios
        if not db.query(Usuario).filter_by(username="admin").first():
            admin = Usuario(
                id=str(uuid.uuid4()),
                username="admin",
                full_name="Gerente de Operaciones",
                pin_hash=get_password_hash("1234"),
                rol="ADMIN",
                tienda_id=tienda.id
            )
            db.add(admin)
            logger.info("Usuario ADMIN Creado: PIN 1234")

        # 3. Categorías con Iconos Visuales (Simulados en el nombre para el Kiosko)
        cat_data = [
            ("Pollos Asados 🔥", "pollos", "/static/assets/minimalist/pollo.png"),
            ("Pizzas Artesanas 🍕", "pizzas", "/static/assets/minimalist/pizza.png"),
            ("Bocadillos & Baguettes 🥖", "bocadillos", "/static/assets/minimalist/bocadillo.png"),
            ("Hamburguesas Pro 🍔", "burgers", "/static/assets/minimalist/burger.png"),
            ("Arroces & Paellas 🥘", "arroz", "/static/assets/minimalist/arroz.png"),
            ("Sándwiches & Snacks 🥪", "sandwiches", "/static/assets/minimalist/sandwich.png"),
            ("Bebidas Frías 🥤", "bebidas", "/static/assets/minimalist/refresco.png"),
            ("Combos Ahorro 🛍️", "combos", "/static/assets/minimalist/refresco.png"), # Generic
            ("Complementos 🍟", "lados", "/static/assets/minimalist/burger.png"), # Generic
            ("Postres Caseros 🍰", "postres", "/static/assets/minimalist/sandwich.png") # Generic
        ]
        
        categorias = {}
        for nombre, key, img in cat_data:
            c = db.query(Categoria).filter_by(nombre=nombre).first()
            if not c:
                c = Categoria(id=str(uuid.uuid4()), nombre=nombre, imagen_url=img)
                db.add(c)
                db.commit()
            else:
                # Actualizar imagen si ha cambiado o no existía
                c.imagen_url = img
                db.commit()
            categorias[key] = c

        # 4. Catálogo Ultra-Premium
        productos_data = [
            # POLLOS
            {
                "nombre": "Pollo al Carbón de Encina",
                "desc": "Nuestro orgullo. Marinado 24h con 12 especias secretas y asado lentamente.",
                "precio": 15.50,
                "cat": "pollos",
                "img": "https://images.unsplash.com/photo-1598103442097-8b74394b95c6?auto=format&fit=crop&q=80&w=800",
                "alergenos": "Ninguno",
                "nutri": "Proteínas: 25g, Grasas: 12g, Calorías: 210kcal por 100g"
            },
            {
                "nombre": "Medio Pollo Gourmet",
                "desc": "La mitad de nuestro pollo estrella, tierno y jugoso por dentro.",
                "precio": 8.90,
                "cat": "pollos",
                "img": "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?auto=format&fit=crop&q=80&w=800",
                "alergenos": "Ninguno",
                "nutri": "Proteínas: 25g, Calorías: 210kcal"
            },
            # COMBOS
            {
                "nombre": "Pack Familiar Koal",
                "desc": "2 Pollos + 2 Patatas Grandes + Ensalada de la Casa + Bebida 2L.",
                "precio": 38.00,
                "cat": "combos",
                "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&q=80&w=800",
                "alergenos": "Huevo (Salsas), Gluten (Pan)",
                "nutri": "Ideal para 4-6 personas."
            },
            {
                "nombre": "Combo Pareja",
                "desc": "1 Pollo + Patatas Medianas + 2 Bebidas + 2 Postres.",
                "precio": 24.50,
                "cat": "combos",
                "img": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&q=80&w=800",
                "alergenos": "Lactosa (Postre)",
                "nutri": "Cena completa para dos."
            },
            # COMPLEMENTOS
            {
                "nombre": "Patatas Fritas 'Triple Cocción'",
                "desc": "Patata agria seleccionada, cortada a mano y frita en tres tiempos.",
                "precio": 4.50,
                "cat": "lados",
                "img": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?auto=format&fit=crop&q=80&w=800",
                "alergenos": "Ninguno",
                "nutri": "Energía pura."
            },
            {
                "nombre": "Pimientos Asados al Carbón",
                "desc": "Pimientos de temporada asados en la misma parrilla que el pollo.",
                "precio": 5.90,
                "cat": "lados",
                "img": "https://images.unsplash.com/photo-1516824467205-aba65913550e?auto=format&fit=crop&q=80&w=800",
                "alergenos": "Ninguno",
                "nutri": "Fibra y sabor."
            },
            # BEBIDAS
            {
                "nombre": "Refresco Coca-Cola 33cl",
                "desc": "Bebida refrescante clásica.",
                "precio": 2.20,
                "cat": "bebidas",
                "img": "/static/assets/minimalist/refresco.png",
                "alergenos": "Ninguno",
                "nutri": "Contiene azúcar."
            },
            # PIZZAS
            {
                "nombre": "Pizza Margarita Minimal",
                "desc": "Mozzarella, tomate y albahaca fresca.",
                "precio": 10.50,
                "cat": "pizzas",
                "img": "/static/assets/minimalist/pizza.png",
                "alergenos": "Gluten, Lactosa",
                "nutri": "Calorías: 250kcal/porción"
            },
            # BOCADILLOS
            {
                "nombre": "Bocadillo de Serranito",
                "desc": "Lomo, jamón, pimiento frito y tomate.",
                "precio": 6.50,
                "cat": "bocadillos",
                "img": "/static/assets/minimalist/bocadillo.png",
                "alergenos": "Gluten",
                "nutri": "Proteína pura."
            },
            # HAMBURGUESAS
            {
                "nombre": "Burger Koal Classic",
                "desc": "Ternera premium, queso, lechuga y salsa secreta.",
                "precio": 12.00,
                "cat": "burgers",
                "img": "/static/assets/minimalist/burger.png",
                "alergenos": "Gluten, Lactosa",
                "nutri": "Sabor intenso."
            },
            # ARROZ
            {
                "nombre": "Arroz con Pollo",
                "desc": "Arroz tradicional cocinado con el jugo de nuestros pollos.",
                "precio": 9.50,
                "cat": "arroz",
                "img": "/static/assets/minimalist/arroz.png",
                "alergenos": "Ninguno",
                "nutri": "Carbohidratos complejos."
            },
            # SANDWICH
            {
                "nombre": "Sandwich Mixto",
                "desc": "Jamón york y queso fundido.",
                "precio": 4.50,
                "cat": "sandwiches",
                "img": "/static/assets/minimalist/sandwich.png",
                "alergenos": "Gluten, Lactosa",
                "nutri": "Ligero."
            }
        ]

        for p_data in productos_data:
            existing = db.query(Producto).filter_by(nombre=p_data["nombre"]).first()
            if not existing:
                p = Producto(
                    id=str(uuid.uuid4()),
                    nombre=p_data["nombre"],
                    descripcion=p_data["desc"],
                    precio=p_data["precio"],
                    categoria_id=categorias[p_data["cat"]].id,
                    tienda_id=tienda.id,
                    stock_actual=100,
                    imagen_url=p_data["img"],
                    alergenos=p_data["alergenos"],
                    info_nutricional=p_data["nutri"],
                    is_active=True
                )
                db.add(p)
        
        db.commit()
        logger.info(f"Catálogo de {len(productos_data)} productos sembrado.")
        logger.info("[SUCCESS] Mega Seeder Industrial Completado.")

    except Exception as e:
        db.rollback()
        logger.error(f"[ERROR] Sembrado fallido: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        except Exception:
            pass
    seed_ultra_industrial()
