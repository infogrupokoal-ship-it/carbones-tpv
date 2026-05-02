from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import Pedido, ItemPedido, Producto, Usuario, Cliente, Referido
from datetime import datetime, timedelta
import random

def seed_enterprise_data():
    db = SessionLocal()
    try:
        print("Starting Seeding Enterprise Singularity Data...")
        
        # 1. Ensure we have products
        pollos = db.query(Producto).all()
        if not pollos:
            print("No products found, skipping order seeding.")
            return

        # 2. Seed historical orders for the last 30 days
        for i in range(30):
            date = datetime.now() - timedelta(days=i)
            num_orders = random.randint(10, 30)
            
            for _ in range(num_orders):
                order_time = date.replace(hour=random.randint(11, 23), minute=random.randint(0, 59))
                p = Pedido(
                    fecha=order_time,
                    estado="COMPLETADO",
                    total=0,
                    metodo_pago=random.choice(["EFECTIVO", "TARJETA", "STRIPE"]),
                    numero_ticket=f"TKT-{i}-{random.randint(1000, 9999)}"
                )
                db.add(p)
                db.flush()
                
                # Add 1-4 items
                total = 0
                for _ in range(random.randint(1, 4)):
                    prod = random.choice(pollos)
                    item = ItemPedido(
                        pedido_id=p.id,
                        producto_id=prod.id,
                        cantidad=random.randint(1, 3),
                        precio_unitario=prod.precio
                    )
                    total += item.cantidad * item.precio_unitario
                    db.add(item)
                
                p.total = total
        
        # 3. Seed some referrals
        for _ in range(50):
            r = Referido(
                codigo=f"REF-{random.randint(100, 999)}",
                estado=random.choice(["PENDIENTE", "COMPLETADO", "EXPIRADO"]),
                fecha_creacion=datetime.now() - timedelta(days=random.randint(1, 60)),
                bono_aplicado=random.choice([5, 10, 0])
            )
            db.add(r)

        db.commit()
        print("Enterprise Data Seeded Successfully.")
    except Exception as e:
        print(f"Seeding Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_enterprise_data()
