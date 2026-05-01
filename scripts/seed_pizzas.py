from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models import Categoria, Producto

DB_PATH = "sqlite:///tpv_data.sqlite"
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_pizzas():
    db = SessionLocal()
    try:
        cat_nombre = "PIZZAS ARTESANAS"
        cat = db.query(Categoria).filter(Categoria.nombre == cat_nombre).first()
        if not cat:
            cat = Categoria(nombre=cat_nombre)
            db.add(cat)
            db.flush()

        pizzas_data = [
            {
                "nombre": "PIZZA MARGARITA",
                "desc": "Salsa de tomate casera, extra de queso mozzarella y orégano",
                "precio": 7.50
            },
            {
                "nombre": "PIZZA PROSCIUTTO",
                "desc": "Salsa de tomate, queso mozzarella, jamón york de primera y orégano",
                "precio": 8.50
            },
            {
                "nombre": "PIZZA CUATRO QUESOS",
                "desc": "Salsa de tomate y mezcla de 4 quesos fundidos (mozzarella, gorgonzola, emmental y roquefort)",
                "precio": 9.50
            },
            {
                "nombre": "PIZZA BARBACOA",
                "desc": "Salsa barbacoa especial, queso mozzarella, carne picada de ternera y bacon crujiente",
                "precio": 9.50
            },
            {
                "nombre": "PIZZA CARBONARA",
                "desc": "Base de nata, queso mozzarella, bacon ahumado, cebolla y champiñones",
                "precio": 9.00
            },
            {
                "nombre": "PIZZA PEPPERONI",
                "desc": "Salsa de tomate, queso mozzarella y pepperoni ligeramente picante",
                "precio": 8.50
            },
            {
                "nombre": "PIZZA VEGETAL",
                "desc": "Salsa de tomate, queso mozzarella, champiñones frescos, pimiento rojo y verde, cebolla y aceitunas",
                "precio": 8.50
            }
        ]

        for pdata in pizzas_data:
            prod = db.query(Producto).filter(Producto.nombre == pdata["nombre"]).first()
            if not prod:
                prod = Producto(
                    nombre=pdata["nombre"],
                    descripcion=pdata["desc"],
                    precio=pdata["precio"],
                    categoria_id=cat.id,
                    stock_actual=50,
                    is_active=True,
                )
                db.add(prod)
            else:
                prod.descripcion = pdata["desc"]
                prod.precio = pdata["precio"]
                prod.categoria_id = cat.id
                prod.is_active = True

        db.commit()
        print("Pizzas inyectadas con exito.")
    except Exception as e:
        print(f"Error al inyectar pizzas: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_pizzas()
