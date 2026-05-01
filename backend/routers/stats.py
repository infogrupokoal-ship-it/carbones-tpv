from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta
from typing import Dict, List, Any
from pydantic import BaseModel, Field

from .admin_audit import log_audit_action
from ..database import get_db
from ..models import Pedido, ItemPedido, Producto, Cliente, ReporteZ, Review, MovimientoStock

router = APIRouter(prefix="/stats", tags=["Business Intelligence"])

class DashboardKPIs(BaseModel):
    ventas_hoy: float
    pedidos_count: int
    ticket_medio: float
    coste_mermas: float
    envios_hoy: int
    satisfaccion: float

class DashboardData(BaseModel):
    kpis: DashboardKPIs
    charts: Dict[str, Any]
    reviews: List[Dict[str, Any]]
    recent_orders: List[Dict[str, Any]]
    stock_alerts: List[Dict[str, Any]]
    status: str = "operational"

@router.get("/dashboard", response_model=DashboardData)
def get_unified_dashboard(db: Session = Depends(get_db)):
    """
    Motor de Inteligencia Centralizado: Proporciona telemetría operativa y financiera
    para todos los niveles de mando de la organización.
    """
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")
    
    # 1. KPIs de Alto Nivel
    ventas_hoy = db.query(func.sum(Pedido.total)).filter(func.date(Pedido.fecha) == today).scalar() or 0.0
    num_pedidos = db.query(func.count(Pedido.id)).filter(func.date(Pedido.fecha) == today).scalar() or 0
    envios_hoy = db.query(Pedido).filter(func.date(Pedido.fecha) == today, Pedido.metodo_envio == "DOMICILIO").count()
    
    # Mermas (valoradas al 40% del PVP)
    mermas_hoy = db.query(func.sum(MovimientoStock.cantidad * Producto.precio * 0.4))\
        .join(Producto)\
        .filter(MovimientoStock.tipo == "SOBRANTE_DIA")\
        .filter(func.date(MovimientoStock.fecha) == today).scalar() or 0.0
        
    satisfaccion = db.query(func.avg(Review.rating)).scalar() or 5.0

    # 2. Análisis de Tendencias (Histórico 7 días)
    end_date = today
    start_date = end_date - timedelta(days=6)
    history = db.query(func.date(Pedido.fecha).label("day"), func.sum(Pedido.total))\
        .filter(func.date(Pedido.fecha) >= start_date)\
        .group_by("day").order_by("day").all()
    
    # 3. Rendimiento por Horas (Hoy)
    horas_labels = [f"{h:02d}:00" for h in range(11, 24)] # Horario operativo estándar
    ventas_horas = db.query(
        func.strftime("%H", Pedido.fecha).label("hora"),
        func.sum(Pedido.total)
    ).filter(func.date(Pedido.fecha) == today).group_by("hora").all()
    
    horas_dict = {f"{int(h):02d}:00": v for h, v in ventas_horas}
    horas_data = [horas_dict.get(h, 0.0) for h in horas_labels]

    # 4. Top Productos (Categorizados)
    def get_top_products(cat_name=None):
        query = db.query(Producto.nombre, func.sum(ItemPedido.cantidad).label("qty"))\
            .join(ItemPedido).join(Pedido)\
            .filter(func.date(Pedido.fecha) == today)
        if cat_name:
            query = query.join(Producto.categoria).filter(Producto.categoria.has(nombre=cat_name))
        return query.group_by(Producto.nombre).order_by(func.desc("qty")).limit(5).all()

    top_pollos = get_top_products("Pollos Asados")
    top_pizzas = get_top_products("Pizzas")

    # 5. Reviews Recientes
    recent_reviews = db.query(Review).order_by(Review.fecha.desc()).limit(10).all()
    reviews_list = [{
        "rating": r.rating,
        "comentario": r.comentario,
        "fecha": r.fecha.strftime("%H:%M") if r.fecha else "--:--",
        "cliente": "Anónimo"
    } for r in recent_reviews]

    # 6. Pedidos Recientes (Live Feed)
    recent_orders = db.query(Pedido).order_by(Pedido.fecha.desc()).limit(15).all()
    orders_list = [{
        "id": o.id,
        "numero_ticket": o.numero_ticket,
        "total": o.total,
        "metodo_pago": o.metodo_pago,
        "metodo_envio": o.metodo_envio,
        "estado": o.estado,
        "fecha": o.fecha.strftime("%H:%M:%S"),
        "cliente_nombre": o.cliente.nombre if o.cliente else "Anon",
        "cliente_telefono": o.cliente.telefono if o.cliente else None,
        "items": [it.producto_id for it in o.items]
    } for o in recent_orders]

    # 7. Alertas de Stock (Bajo Mínimo)
    stock_alerts = db.query(Producto).filter(Producto.stock_actual <= Producto.stock_minimo).limit(10).all()
    alerts_list = [{
        "nombre": p.nombre,
        "stock_actual": p.stock_actual,
        "stock_minimo": p.stock_minimo
    } for p in stock_alerts]

    return DashboardData(
        kpis=DashboardKPIs(
            ventas_hoy=round(ventas_hoy, 2),
            pedidos_count=num_pedidos,
            ticket_medio=round(ventas_hoy / num_pedidos, 2) if num_pedidos > 0 else 0,
            coste_mermas=round(abs(mermas_hoy), 2),
            envios_hoy=envios_hoy,
            satisfaccion=round(float(satisfaccion), 1)
        ),
        charts={
            "historico": {
                "labels": [h[0].strftime("%d/%m") for h in history],
                "data": [round(h[1], 2) for h in history]
            },
            "horas": {
                "labels": horas_labels,
                "data": [round(v, 2) for v in horas_data]
            },
            "top_pollos": {
                "labels": [p[0] for p in top_pollos],
                "data": [int(p[1]) for p in top_pollos]
            },
            "top_pizzas": {
                "labels": [p[0] for p in top_pizzas],
                "data": [int(p[1]) for p in top_pizzas]
            }
        },
        reviews=reviews_list,
        recent_orders=orders_list,
        stock_alerts=alerts_list
    )

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
