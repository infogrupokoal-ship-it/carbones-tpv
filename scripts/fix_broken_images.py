from backend.database import SessionLocal
from backend.models import Producto

def fix_broken_images():
    db = SessionLocal()
    try:
        # Pimientos asados broken image
        broken_pimientos = "https://images.unsplash.com/photo-1516824467205-aba65913550e"
        fixed_pimientos = "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d" # Roasted veggies
        
        prod_pim = db.query(Producto).filter(Producto.imagen_url.contains("1516824467205")).first()
        if prod_pim:
            prod_pim.imagen_url = prod_pim.imagen_url.replace(broken_pimientos, fixed_pimientos)
        
        # Any other broken image fallback
        broken_chicken = "https://images.unsplash.com/photo-1598514982205-f36b96d1e8dd"
        fixed_chicken = "https://images.unsplash.com/photo-1598103442097-8b74394b95c6"
        
        prod_chic = db.query(Producto).filter(Producto.imagen_url.contains("1598514982205")).first()
        if prod_chic:
            prod_chic.imagen_url = prod_chic.imagen_url.replace(broken_chicken, fixed_chicken)

        db.commit()
        print("✅ Imágenes rotas corregidas en DB.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error corrigiendo imágenes: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_broken_images()
