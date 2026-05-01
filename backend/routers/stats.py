from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta
from typing import Dict, List, Any
from pydantic import BaseModel, Field

from ..database import get_db
from ..models import Pedido, ItemPedido, Producto, Cliente, ReporteZ

router = APIRouter(prefix="/stats", tags=["Business Intelligence"])

@router.get("/summary")
def get_daily_summary(db: Session = Depends(get_db)):
    """
    Resumen ejecutivo diario para el Dashboard BI.
    """
    today = date.today()
    
    # Ventas totales hoy
    ventas_hoy = db.query(func.sum(Pedido.total)).filter(func.date(Pedido.fecha) == today).scalar() or 0.0
    num_pedidos = db.query(func.count(Pedido.id)).filter(func.date(Pedido.fecha) == today).scalar() or 0
    
    # Top 5 Productos hoy
    top_productos = (
        db.query(Producto.nombre, func.sum(ItemPedido.cantidad).label("total_qty"))
        .join(ItemPedido, ItemPedido.producto_id == Producto.id)
        .join(Pedido, ItemPedido.pedido_id == Pedido.id)
        .filter(func.date(Pedido.fecha) == today)
        .group_by(Producto.nombre)
        .order_by(func.desc("total_qty"))
        .limit(5)
        .all()
    )
    
    # Distribución de pago
    pagos = (
        db.query(Pedido.metodo_pago, func.count(Pedido.id))
        .filter(func.date(Pedido.fecha) == today)
        .group_by(Pedido.metodo_pago)
        .all()
    )
    
    # Estado de Cocina
    estados = (
        db.query(Pedido.estado, func.count(Pedido.id))
        .filter(func.date(Pedido.fecha) == today)
        .group_by(Pedido.estado)
        .all()
    )

    return {
        "ventas_total": round(ventas_hoy, 2),
        "pedidos_count": num_pedidos,
        "ticket_medio": round(ventas_hoy / num_pedidos, 2) if num_pedidos > 0 else 0,
        "top_productos": [{"nombre": p[0], "cantidad": p[1]} for p in top_productos],
        "metodos_pago": {p[0]: p[1] for p in pagos},
        "estados_cocina": {e[0]: e[1] for e in estados},
        "build_marker": "INDUSTRIAL-ULTRA-2026-04-30"
    }

@router.get("/history")
def get_sales_history(days: int = 7, db: Session = Depends(get_db)):
    """
    Histórico de ventas para gráficas de tendencia.
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    
    history = (
        db.query(func.date(Pedido.fecha).label("day"), func.sum(Pedido.total))
        .filter(func.date(Pedido.fecha) >= start_date)
        .group_by("day")
        .order_by("day")
        .all()
    )
    
    return {
        "labels": [h[0].strftime("%Y-%m-%d") for h in history],
        "data": [round(h[1], 2) for h in history]
    }

class CierreZRequest(BaseModel):
    efectivo_declarado: float = Field(0.0, description="Efectivo contado físicamente en caja")

@router.post("/cierre-z")
def generar_cierre_z(req: CierreZRequest, db: Session = Depends(get_db)):
    """
    Genera el Reporte de Cierre Z Digital (Fin de día).
    Calcula ventas, desglosa pagos, descuadre de caja y sella el día operativo.
    Utiliza el ReportingService para automatizar mermas y notificaciones.
    """
    from ..services.reporting import ReportingService
    try:
        # La lógica industrial (Mermas, PDF, WhatsApp, Guardado) está encapsulada en ReportingService
        reporte = ReportingService.generar_cierre_z(db, req.efectivo_declarado)
        
        # Registrar Auditoría
        from .admin_audit import log_audit_action
        log_audit_action(
            db, 
            usuario_id=None, 
            accion="CIERRE_Z", 
            entidad="FINANZAS", 
            entidad_id=reporte.id, 
            payload_nuevo=f"Descuadre: {reporte.diferencia}"
        )
        
        return {
            "status": "success",
            "reporte_id": reporte.id,
            "resumen": reporte.resumen_texto,
            "diferencia": reporte.diferencia,
            "efectivo_teorico": reporte.total_efectivo
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Error generando Cierre Z: {str(e)}")
