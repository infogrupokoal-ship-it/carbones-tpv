import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Categoria, Producto, Usuario, Review

DB_PATH = "sqlite:///tpv_data.sqlite"

def reset_db():
    print("Iniciando Hard Reset de la Base de Datos...")
    engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
    
    # Dropping all tables to ensure a clean slate
    Base.metadata.drop_all(bind=engine)
    print("Tablas antiguas eliminadas.")
    
    # Creating tables with new schema
    Base.metadata.create_all(bind=engine)
    print("Nuevas tablas creadas.")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("Insertando Usuarios...")
        db.add_all([
            Usuario(username="encargado_mañana", password="123", rol="MANANA"),
            Usuario(username="encargado_tarde", password="123", rol="TARDE"),
            Usuario(username="admin", password="123", rol="ADMIN"),
            Usuario(username="cocina", password="123", rol="COCINA"),
        ])
        
        print("Insertando Categorías (Pizzas, Pollos Asados, Noche, etc.)...")
        cat_pollos = Categoria(nombre="Pollos Asados", orden=1)
        cat_pizzas = Categoria(nombre="Pizzas Artesanas", orden=2)
        cat_guarniciones = Categoria(nombre="Guarniciones", orden=3)
        cat_bebidas = Categoria(nombre="Bebidas", orden=4)
        cat_noche_bocadillos = Categoria(nombre="Bocadillos Noche", orden=5)
        cat_noche_especiales = Categoria(nombre="Especiales de la Casa (Noche)", orden=6)
        cat_salsas = Categoria(nombre="Salsas y Extras", orden=7)
        
        db.add_all([cat_pollos, cat_pizzas, cat_guarniciones, cat_bebidas, cat_noche_bocadillos, cat_noche_especiales, cat_salsas])
        db.flush()
        
        print("Insertando Lógica Fraccional de Pollos...")
        # 100 cuartos = 25 pollos enteros
        pollo_base = Producto(nombre="[MATERIA] Pollo Base", precio=0, categoria_id=None, is_active=False, stock_actual=100)
        db.add(pollo_base)
        db.flush()
        
        p_entero = Producto(nombre="Pollo Entero", precio=12.00, categoria_id=cat_pollos.id, stock_base_id=pollo_base.id, factor_stock=4, url_imagen="/static/img/pollo_entero.jpg", descripcion="Pollo asado entero jugoso con especias secretas.", alergenos="")
        p_medio = Producto(nombre="Medio Pollo", precio=6.50, categoria_id=cat_pollos.id, stock_base_id=pollo_base.id, factor_stock=2, url_imagen="/static/img/medio_pollo.jpg", alergenos="")
        p_cuarto = Producto(nombre="Cuarto de Pollo", precio=3.50, categoria_id=cat_pollos.id, stock_base_id=pollo_base.id, factor_stock=1, url_imagen="/static/img/cuarto_pollo.jpg", alergenos="")
        
        print("Insertando Productos Base (Pizzas, Guarniciones, con alergenos)...")
        prod_pizza_1 = Producto(nombre="Pizza Margarita", precio=8.00, categoria_id=cat_pizzas.id, stock_actual=50, descripcion="Clásica mozzarella y tomate.", alergenos="Gluten, Lácteos")
        prod_pizza_2 = Producto(nombre="Pizza Barbacoa", precio=10.00, categoria_id=cat_pizzas.id, stock_actual=40, descripcion="Salsa barbacoa, carne picada, bacon.", alergenos="Gluten, Lácteos, Soja")
        prod_pizza_3 = Producto(nombre="Pizza Cuatro Quesos", precio=11.00, categoria_id=cat_pizzas.id, stock_actual=30, alergenos="Gluten, Lácteos")
        
        prod_patatas = Producto(nombre="Patatas Fritas Grandes", precio=4.00, categoria_id=cat_guarniciones.id, stock_actual=100, descripcion="Ración generosa.", alergenos="")
        prod_croquetas = Producto(nombre="Ración de Croquetas", precio=5.00, categoria_id=cat_guarniciones.id, stock_actual=80, descripcion="Caseras de jamón.", alergenos="Gluten, Lácteos, Huevo")
        
        prod_refresco = Producto(nombre="Refresco Cola", precio=1.80, categoria_id=cat_bebidas.id, stock_actual=200)
        prod_cerveza = Producto(nombre="Lata de Cerveza", precio=2.00, categoria_id=cat_bebidas.id, stock_actual=200, alergenos="Gluten")
        
        prod_bocadillo_1 = Producto(nombre="Chivito", precio=6.50, categoria_id=cat_noche_bocadillos.id, stock_actual=30, alergenos="Gluten, Huevo, Lácteos")
        prod_bocadillo_2 = Producto(nombre="Brascada", precio=7.00, categoria_id=cat_noche_bocadillos.id, stock_actual=30, alergenos="Gluten")
        
        # Salsas y addons
        prod_salsa_alioli = Producto(nombre="Salsa Alioli", precio=0.50, categoria_id=cat_salsas.id, is_addon=True, stock_actual=100, alergenos="Huevo")
        prod_salsa_brava = Producto(nombre="Salsa Brava", precio=0.50, categoria_id=cat_salsas.id, is_addon=True, stock_actual=100)
        
        db.add_all([
            p_entero, p_medio, p_cuarto,
            prod_pizza_1, prod_pizza_2, prod_pizza_3,
            prod_patatas, prod_croquetas,
            prod_refresco, prod_cerveza,
            prod_bocadillo_1, prod_bocadillo_2,
            prod_salsa_alioli, prod_salsa_brava
        ])
        db.flush()
        
        print("Insertando Reviews de Ejemplo para Dashboard...")
        rev1 = Review(rating=5, comentario="¡Los pollos asados están espectaculares! El servicio muy rápido.", analisis_ia="Sentimiento positivo, destaca calidad y velocidad.")
        rev2 = Review(rating=2, comentario="La pizza cuatro quesos estaba un poco quemada por los bordes y me sentó pesada.", analisis_ia="Sentimiento negativo, menciona defecto en producto (quemado) y queja digestiva. CRITICA.")
        db.add_all([rev1, rev2])
        
        db.commit()
        print("¡Hard Reset y Seed Completados con Éxito!")
        
    except Exception as e:
        db.rollback()
        print("Error durante el seed:", e)
    finally:
        db.close()

if __name__ == "__main__":
    reset_db()
