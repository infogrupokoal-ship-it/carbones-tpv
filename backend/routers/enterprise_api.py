from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Pedido, Producto, Tienda
from typing import List, Optional

router = APIRouter(prefix="/api/v1/enterprise", tags=["Enterprise Singularity API"])

def verify_api_key(x_api_key: str = Header(...)):
    """Validación de API Key para integraciones B2B."""
    if x_api_key != "TPV-ENTERPRISE-MASTER-KEY-2026":
        raise HTTPException(status_code=403, detail="Invalid Enterprise API Key")
    return x_api_key

@router.get("/inventory/global")
def get_global_inventory(db: Session = Depends(get_db), key: str = Depends(verify_api_key)):
    """Exporta el inventario consolidado para partners B2B."""
    from backend.models import Ingrediente
    items = db.query(Ingrediente).all()
    return [{"id": i.id, "sku": i.nombre, "stock": i.stock_actual, "unit": i.unidad_medida} for i in items]

@router.post("/orders/external")
def create_external_order(order_data: dict, db: Session = Depends(get_db), key: str = Depends(verify_api_key)):
    """Permite a agregadores externos inyectar pedidos directamente en el KDS."""
    # Lógica de creación simplificada
    new_order = Pedido(
        numero_ticket=f"EXT-{order_data.get('partner_id')}-{random.randint(100,999)}",
        total=order_data.get('total'),
        estado="PENDIENTE",
        metodo_pago="EXT_PARTNER"
    )
    db.add(new_order)
    db.commit()
    return {"status": "injected", "ticket": new_order.numero_ticket}

@router.get("/analytics/snapshot")
def get_financial_snapshot(db: Session = Depends(get_db), key: str = Depends(verify_api_key)):
    """Métricas financieras de alto nivel para inversores (API-Only)."""
    from backend.models import FinancialSnapshot
    snap = db.query(FinancialSnapshot).order_by(FinancialSnapshot.timestamp.desc()).first()
    return snap
