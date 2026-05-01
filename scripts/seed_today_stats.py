import sys
import os
from datetime import datetime, date, timedelta
import random

# Añadir el directorio raíz al path para importar el backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, engine
from backend.models import Pedido, ItemPedido, Producto, Review, MovimientoStock

def seed_today():
    db = SessionLocal()
    try:
        today = datetime.now()
        print(f"SEED: Sembrando datos para hoy: {today.date()}")
        
        # 1. Obtener productos para los items
        productos = db.query(Producto).all()
        if not productos:
            print("ERROR: No hay productos en la DB. Ejecuta el seeder general primero.")
            return

        # 2. Generar 10-15 pedidos para hoy
        for i in range(random.randint(10, 15)):
            ticket = f"TKT-TODAY-{i:03d}"
            # Horas aleatorias entre las 12:00 y las 22:00
            fecha_pedido = today.replace(hour=random.randint(12, 21), minute=random.randint(0, 59))
            
            pedido = Pedido(
                numero_ticket=ticket,
                fecha=fecha_pedido,
                estado="COMPLETADO",
                metodo_pago=random.choice(["EFECTIVO", "TARJETA"]),
                metodo_envio=random.choice(["LOCAL", "DOMICILIO"]),
                total=0.0
            )
            db.add(pedido)
            db.flush() # Para obtener el ID

            # Añadir 1-4 items por pedido
            subtotal = 0.0
            for _ in range(random.randint(1, 4)):
                p = random.choice(productos)
                qty = random.randint(1, 2)
                item = ItemPedido(
                    pedido_id=pedido.id,
                    producto_id=p.id,
                    cantidad=qty,
                    precio_unitario=p.price if hasattr(p, 'price') else p.precio
                )
                db.add(item)
                subtotal += (item.precio_unitario * qty)
            
            pedido.total = subtotal
            
        # 3. Generar algunas reviews para hoy
        comentarios = [
            "El pollo estaba increible!",
            "La pizza llego un poco fria, pero de sabor excelente.",
            "Servicio de 10, Carbonito me ayudo mucho.",
            "Mejor TPV de la zona, muy rapido.",
            "Las patatas fritas son adictivas."
        ]
        for _ in range(5):
            review = Review(
                cliente_id=None,
                rating=random.randint(4, 5),
                comentario=random.choice(comentarios),
                fecha=today
            )
            db.add(review)

        # 4. Generar mermas (SOBRANTE_DIA) para que el KPI de mermas se mueva
        for _ in range(3):
            p = random.choice(productos)
            mov = MovimientoStock(
                producto_id=p.id,
                cantidad=-random.randint(1, 5),
                tipo="SOBRANTE_DIA",
                fecha=today,
                descripcion="Ajuste fin de jornada (Demo)"
            )
            db.add(mov)

        db.commit()
        print("SUCCESS: Datos de hoy sembrados exitosamente.")
    except Exception as e:
        print(f"CRITICAL ERROR en seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_today()
