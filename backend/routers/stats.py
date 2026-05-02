from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models import Pedido, Presupuesto, Referido
from datetime import datetime, timedelta

router = APIRouter(prefix="/stats", tags=["Business Intelligence"])

@router.get("/commercial-funnel")
def get_funnel(db: Session = Depends(get_db)):
    """Retorna datos para el embudo de ventas: Presupuestos -> Pedidos"""
    total_quotes = db.query(Presupuesto).count()
    accepted_quotes = db.query(Presupuesto).filter(Presupuesto.estado == "ACEPTADO").count()
    total_orders = db.query(Pedido).count()
    
    return {
        "presupuestos_totales": total_quotes,
        "presupuestos_aceptados": accepted_quotes,
        "pedidos_totales": total_orders,
        "conversion_quote_to_order": (accepted_quotes / total_quotes * 100) if total_quotes > 0 else 0
    }

@router.get("/growth-metrics")
def get_growth(db: Session = Depends(get_db)):
    """Métricas de crecimiento viral (referidos)"""
    total_referrals = db.query(Referido).count()
    completed_referrals = db.query(Referido).filter(Referido.estado == "COMPLETADO").count()
    
    # ROI estimado (asumiendo ticket promedio de 30€ y bono de 5€)
    total_bonos = db.query(func.sum(Referido.bono_aplicado)).scalar() or 0
    estimated_revenue = completed_referrals * 30
    roi = (estimated_revenue / total_bonos) if total_bonos > 0 else 0
    
    return {
        "referidos_totales": total_referrals,
        "referidos_exitosos": completed_referrals,
        "roi_marketing": round(roi, 2),
        "ahorro_adquisicion": completed_referrals * 10 # 10€ ahorro vs Ads
    }

@router.get("/daily-sales")
def get_daily_sales(db: Session = Depends(get_db)):
    """Ventas de los últimos 7 días"""
    today = datetime.now()
    today - timedelta(days=7)
    
    # Simulado por ahora ya que el modelo Pedido necesita fecha
    # En un entorno real se agruparía por func.date(Pedido.creado_en)
    return [
        {"dia": "Lun", "ventas": 450},
        {"dia": "Mar", "ventas": 520},
        {"dia": "Mie", "ventas": 380},
        {"dia": "Jue", "ventas": 610},
        {"dia": "Vie", "ventas": 890},
        {"dia": "Sab", "ventas": 1200},
        {"dia": "Dom", "ventas": 950}
    ]
@router.get("/dashboard")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Resumen unificado para el Dashboard BI v5.0"""
    try:
        # 1. KPIs
        ventas_hoy = db.query(func.sum(Pedido.total)).filter(func.date(Pedido.fecha) == datetime.now().date()).scalar() or 0
        pedidos_hoy = db.query(Pedido).filter(func.date(Pedido.fecha) == datetime.now().date()).count()
        
        # 2. Gráfica de Ventas por Horas (Simulado o real)
        # En una app real haríamos un group_by por hora
        horas_labels = ["09:00", "11:00", "13:00", "15:00", "17:00", "19:00", "21:00"]
        horas_data = [50, 120, 450, 320, 80, 210, 540]
        
        # 3. Top Productos (Basado en Pedidos)
        # Aquí simplificamos, en real uniríamos con ItemPedido
        top_labels = ["Pollo Asado XL", "Patatas Fritas", "Menú Familiar", "Croquetas Caseras"]
        top_data = [45, 38, 24, 19]

        # 4. Alertas de Stock (Críticas)
        # Simulado por ahora
        alerts = [
            {"item": "Pollo Fresco", "stock": 5, "min": 20},
            {"item": "Aceite Girasol", "stock": 2, "min": 10}
        ]

        # 5. Pedidos Recientes
        recent = db.query(Pedido).order_by(Pedido.fecha.desc()).limit(5).all()
        recent_mapped = []
        for r in recent:
            recent_mapped.append({
                "id": r.id,
                "cliente": r.cliente.nombre if r.cliente else "Anónimo",
                "total": r.total,
                "estado": r.estado,
                "fecha": r.fecha.strftime("%H:%M")
            })

        return {
            "kpis": {
                "ventas_hoy": float(ventas_hoy),
                "pedidos_count": pedidos_hoy,
                "satisfaccion": 4.8
            },
            "charts": {
                "horas": {"labels": horas_labels, "data": horas_data},
                "top_pollos": {"labels": top_labels, "data": top_data}
            },
            "recent_orders": recent_mapped,
            "stock_alerts": alerts
        }
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {"error": str(e)}
