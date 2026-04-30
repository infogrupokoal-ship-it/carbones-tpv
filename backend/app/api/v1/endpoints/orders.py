from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ....core.database import get_db
from ....models.order import Pedido, ItemPedido
from ..deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[Any])
def get_orders(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Pedido).order_by(Pedido.fecha.desc()).all()

@router.post("/", status_code=21)
def create_order(
    *,
    db: Session = Depends(get_db),
    total: float,
    items: List[dict],
    cliente_id: str = None
):
    import uuid
    new_order = Pedido(
        id=str(uuid.uuid4()),
        numero_ticket=f"TKT-{uuid.uuid4().hex[:6].upper()}",
        total=total,
        base_imponible=total / 1.10,
        iva_total=total - (total / 1.10),
        cliente_id=cliente_id
    )
    db.add(new_order)
    db.commit()
    
    # Agregar items (Simplificado para el demo)
    for item in items:
        db.add(ItemPedido(
            id=str(uuid.uuid4()),
            pedido_id=new_order.id,
            producto_id=item.get("id"),
            cantidad=item.get("cantidad", 1),
            precio_unitario=item.get("precio")
        ))
    db.commit()
    return new_order
