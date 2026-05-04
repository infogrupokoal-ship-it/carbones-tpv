import sys
import os

# Asegurar que el path incluya el directorio raíz del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import Pedido, ItemPedido, PrintQueue

def factory_reset():
    """
    Purga todas las transacciones operativas (pedidos, items de pedido y cola de impresión)
    sin afectar el catálogo maestro (productos, categorías, usuarios).
    Ideal para limpiar la base de datos tras las pruebas y antes de pasar a Producción Real.
    """
    db = SessionLocal()
    print("[FACTORY RESET] Iniciando purga de transacciones de prueba...")
    try:
        deleted_items = db.query(ItemPedido).delete()
        deleted_pedidos = db.query(Pedido).delete()
        deleted_prints = db.query(PrintQueue).delete()
        db.commit()
        print(f"[FACTORY RESET] Éxito. Purgados:")
        print(f"  - {deleted_pedidos} pedidos")
        print(f"  - {deleted_items} items de pedido")
        print(f"  - {deleted_prints} trabajos de impresión")
        print("[FACTORY RESET] El catálogo de productos y usuarios permanece INTACTO.")
    except Exception as e:
        db.rollback()
        print(f"[FACTORY RESET] Error crítico durante la purga: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    confirmacion = input("¿Estás seguro de que quieres BORRAR todos los pedidos e historial? (escribe 'SI' para confirmar): ")
    if confirmacion == 'SI':
        factory_reset()
    else:
        print("Operación cancelada.")
