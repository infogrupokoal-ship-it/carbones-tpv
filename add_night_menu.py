import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Categoria, Producto

DB_PATH = "sqlite:///tpv_data.sqlite"
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_night_menu():
    db = SessionLocal()
    try:
        cat_night = db.query(Categoria).filter(Categoria.nombre == "Turno Noche").first()
        if not cat_night:
            cat_night = Categoria(nombre="Turno Noche", orden=4)
            db.add(cat_night)
            db.flush()
            
            prod1 = Producto(nombre="Bocadillo de Pollo", descripcion="Bocadillo especial de Pollo Asado y salsa", precio=4.50, categoria_id=cat_night.id, stock_actual=20)
            prod2 = Producto(nombre="Hamburguesa Carbones", descripcion="Hamburguesa casera doble", precio=6.50, categoria_id=cat_night.id, stock_actual=15)
            prod3 = Producto(nombre="Perrito Caliente", descripcion="Perrito gigante con cebolla crujiente", precio=3.50, categoria_id=cat_night.id, stock_actual=30)
            
            db.add_all([prod1, prod2, prod3])
            db.commit()
            print("Night menu (Turno Noche) seeded successfully!")
        else:
            print("Night menu already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_night_menu()
