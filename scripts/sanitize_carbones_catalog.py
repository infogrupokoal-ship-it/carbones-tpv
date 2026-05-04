import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database import SessionLocal, engine, Base
from backend.models import Producto

def sanitize():
    print("Iniciando Sanitizacion Zero-Touch de Catalogos (Koal -> Carbones)")
    db = SessionLocal()
    try:
        productos = db.query(Producto).all()
        revisados = 0
        renombrados = 0
        eliminados = 0
        
        for p in productos:
            revisados += 1
            nombre = p.nombre
            
            # Chequear nombres prohibidos
            if any(k in nombre for k in ["Koal", "GestionKoal", "GestiónKoal", "Grupo Koal"]):
                # Verificar si ya existe el homonimo de Carbones
                nuevo_nombre = nombre.replace("Koal", "Carbones").replace("Gestion", "").replace("Gestión", "").replace("Grupo ", "").strip()
                
                homonimo = db.query(Producto).filter(Producto.nombre == nuevo_nombre, Producto.id != p.id).first()
                if homonimo:
                    db.delete(p)
                    eliminados += 1
                    print(f"[ELIMINADO DUPLICADO] {nombre}")
                else:
                    p.nombre = nuevo_nombre
                    if p.descripcion and any(k in p.descripcion for k in ["Koal", "GestionKoal", "GestiónKoal", "Grupo Koal"]):
                        p.descripcion = p.descripcion.replace("Koal", "Carbones").replace("GestionKoal", "Carbones").replace("GestiónKoal", "Carbones").replace("Grupo Koal", "Carbones")
                    renombrados += 1
                    print(f"[RENOMBRADO] {nombre} -> {nuevo_nombre}")
                db.commit()

        # Restantes (verificar)
        restantes = db.query(Producto).filter(Producto.nombre.like("%Koal%")).count()
        print("--- RESUMEN ---")
        print(f"Productos revisados: {revisados}")
        print(f"Productos renombrados: {renombrados}")
        print(f"Productos eliminados: {eliminados}")
        print(f"Coincidencias restantes: {restantes}")

        return {
            "revisados": revisados,
            "renombrados": renombrados,
            "eliminados": eliminados,
            "restantes": restantes
        }

    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    sanitize()
