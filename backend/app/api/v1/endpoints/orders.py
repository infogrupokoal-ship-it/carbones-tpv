import uuid
from datetime import datetime
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.core.database import get_db
from backend.app.models.order import Pedido, ItemPedido, Cliente
from backend.app.schemas.order import PedidoCreate, Pedido as PedidoSchema, DashboardKPIs
from backend.app.api.deps import get_current_user, RoleChecker

router = APIRouter()

@router.post("/", response_model=PedidoSchema)
def create_order(
    *,
    db: Session = Depends(get_db),
    order_in: PedidoCreate,
    current_user = Depends(get_current_user)
) -> Any:
    """Crea un nuevo pedido con desglose fiscal automático."""
    nuevo_pedido = Pedido(
        id=str(uuid.uuid4()),
        numero_ticket=f"T-{datetime.now().strftime('%Y%m%d%H%M')}-{str(uuid.uuid4())[:4]}",
        total=order_in.total,
        metodo_pago=order_in.metodo_pago,
        cliente_id=order_in.cliente_id,
        estado="PAGADO" if order_in.metodo_pago else "PENDIENTE"
    )
    
    # Cálculo de IVA (10% por defecto para hostelería)
    nuevo_pedido.base_imponible = round(order_in.total / 1.10, 2)
    nuevo_pedido.iva_total = round(order_in.total - nuevo_pedido.base_imponible, 2)
    
    db.add(nuevo_pedido)
    
    for item in order_in.items:
        db_item = ItemPedido(
            id=str(uuid.uuid4()),
            pedido_id=nuevo_pedido.id,
            producto_id=item.producto_id,
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(nuevo_pedido)
    return nuevo_pedido

@router.get("/", response_model=List[PedidoSchema])
def read_orders(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user)
) -> Any:
    """Lista pedidos con paginación industrial."""
    return db.query(Pedido).offset(skip).limit(limit).all()

@router.get("/kpis", response_model=DashboardKPIs)
def get_dashboard_kpis(
    db: Session = Depends(get_db),
    current_user = Depends(RoleChecker(["ADMIN", "MANAGER"]))
) -> Any:
    """Calcula métricas financieras en tiempo real para gerencia."""
    today = datetime.utcnow().date()
    pedidos_hoy = db.query(Pedido).filter(func.date(Pedido.fecha) == today).all()
    
    total = sum(p.total for p in pedidos_hoy)
    num = len(pedidos_hoy)
    efectivo = sum(p.total for p in pedidos_hoy if p.metodo_pago == "EFECTIVO")
    tarjeta = sum(p.total for p in pedidos_hoy if p.metodo_pago == "TARJETA")
    
    return {
        "total_ventas": total,
        "numero_pedidos": num,
        "ticket_medio": total / num if num > 0 else 0,
        "ventas_efectivo": efectivo,
        "ventas_tarjeta": tarjeta
    }
