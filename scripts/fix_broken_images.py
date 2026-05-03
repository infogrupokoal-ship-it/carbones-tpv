import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import Producto

def fix_broken_images():
    db = SessionLocal()
    try:
        # Update all products with unsplash URLs to use local asset
        productos = db.query(Producto).filter(Producto.imagen_url.contains("unsplash.com")).all()
        count = 0
        for p in productos:
            p.imagen_url = "/static/img/pollo_asado.png"
            count += 1
            
        db.commit()
        print(f"✅ {count} imágenes de productos actualizadas en DB.")
        print("✅ Imágenes rotas corregidas en DB.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error corrigiendo imágenes: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_broken_images()
