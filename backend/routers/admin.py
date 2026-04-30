import uuid
import datetime
import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Producto, Pedido, MovimientoStock, Review, Usuario, Fichaje, ReporteZ, HardwareCommand
from ..services.reporting import ReportingService
from ..ai_agent import ask_asador_ai
from ..utils.logger import logger
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["Gestión Administrativa"])

# --- Esquemas de Datos ---
class ProductoCreate(BaseModel):
    nombre: str
    precio: float
    categoria_id: str
    stock_actual: float = 0

class CierreRequest(BaseModel):
    efectivo_declarado: Optional[float] = None

# --- Endpoints Administrativos ---

@router.get("/dashboard/kpis")
async def get_dashboard_kpis(db: Session = Depends(get_db)):
    """Métricas integrales para el Dashboard de Control Directivo con datos reales."""
    today = datetime.date.today()
    
    # 1. KPIs principales
    ventas_hoy = db.query(func.sum(Pedido.total)).filter(func.date(Pedido.fecha) == today).scalar() or 0.0
    pedidos_count = db.query(Pedido).filter(func.date(Pedido.fecha) == today).count()
    
    # Coste de mermas (Sobrantes de hoy registrados en movimientos)
    mermas_hoy = db.query(func.sum(MovimientoStock.cantidad * Producto.precio * 0.4))\
        .join(Producto)\
        .filter(MovimientoStock.tipo == "SOBRANTE_DIA")\
        .filter(func.date(MovimientoStock.fecha) == today).scalar() or 0.0
        
    avg_rating = db.query(func.avg(Review.rating)).scalar() or 5.0

    # 2. Gráfico de Ventas por Hora (Real)
    # Agrupamos pedidos por hora (usando SQLite strftime)
    ventas_por_hora = db.query(
        func.strftime("%H:00", Pedido.fecha).label("hora"),
        func.sum(Pedido.total).label("total")
    ).filter(func.date(Pedido.fecha) == today)\
     .group_by("hora").order_by("hora").all()

    # 3. Top Productos (Pollos y Pizzas)
    def get_top_by_category(cat_name):
        return db.query(Producto.nombre, func.sum(func.abs(MovimientoStock.cantidad)))\
            .join(MovimientoStock)\
            .join(Producto.categoria)\
            .filter(func.date(MovimientoStock.fecha) == today)\
            .filter(MovimientoStock.tipo == "VENTA")\
            .filter(Producto.categoria.has(nombre=cat_name))\
            .group_by(Producto.nombre)\
            .order_by(func.sum(func.abs(MovimientoStock.cantidad)).desc())\
            .limit(5).all()

    top_pollos = get_top_by_category("Pollos Asados")
    top_pizzas = get_top_by_category("Pizzas")

    # 4. Reviews Recientes
    recent_reviews = db.query(Review).order_by(Review.fecha.desc()).limit(5).all()
    reviews_data = [{
        "rating": r.rating,
        "comentario": r.comentario,
        "fecha": r.fecha.strftime("%H:%M") if r.fecha else "--:--",
        "cliente_nombre": "Cliente TPV"
    } for r in recent_reviews]

    return {
        "kpis": {
            "ventas_hoy": round(ventas_hoy, 2),
            "coste_mermas": round(abs(mermas_hoy), 2),
            "pedidos_b2c": pedidos_count,
            "avg_rating": round(float(avg_rating), 1)
        },
        "charts": {
            "horas": {
                "labels": [v[0] for v in ventas_por_hora] if ventas_por_hora else ["Sin datos hoy"],
                "data": [v[1] for v in ventas_por_hora] if ventas_por_hora else [0]
            },
            "pollos": {
                "labels": [v[0] for v in top_pollos],
                "data": [v[1] for v in top_pollos]
            },
            "pizzas": {
                "labels": [v[0] for v in top_pizzas],
                "data": [v[1] for v in top_pizzas]
            }
        },
        "reviews": reviews_data
    }

@router.post("/trigger_cierre_z")
async def trigger_cierre_z(data: CierreRequest, db: Session = Depends(get_db)):
    """
    Ejecuta el cierre de caja oficial y lo encola para procesamiento de mermas.
    """
    try:
        reporte = ReportingService.generar_cierre_z(db, data.efectivo_declarado)
        return {"status": "success", "msj": "Cierre Z procesado e informado vía WhatsApp.", "report_id": reporte.id}
    except Exception as e:
        logger.error(f"Error en Cierre Z: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai_insights")
async def get_ai_insights(db: Session = Depends(get_db)):
    """Genera insights operativos basados en el estado actual de ventas y stock."""
    try:
        ventas_hoy = db.query(func.sum(Pedido.total)).filter(func.date(Pedido.fecha) == datetime.date.today()).scalar() or 0.0
        reviews = db.query(Review).order_by(Review.fecha.desc()).limit(10).all()
        review_texts = "\n".join([f"- {r.rating}*: {r.comentario}" for r in reviews])
        
        prompt = f"""
        ANALIZA EL ESTADO DE HOY:
        - Ventas Brutas: {ventas_hoy}€
        - Últimas Opiniones:
        {review_texts if review_texts else "Sin opiniones recientes."}
        
        PROPORCIONA:
        1. Un resumen de 2 frases sobre el sentimiento del cliente.
        2. Una recomendación de producción operativa para el próximo turno.
        """
        
        response = await ask_asador_ai(prompt, user_role="analyst")
        
        # Limpieza básica de la respuesta
        parts = response.split("\n\n")
        resumen = parts[0] if len(parts) > 0 else "Análisis preliminar positivo."
        sugerencia = parts[1] if len(parts) > 1 else "Continuar con el ritmo de producción estándar."
        
        return {
            "resumen_reviews": resumen.replace("Koal-AI:", "").strip(),
            "sugerencia_produccion": sugerencia.strip()
        }
    except Exception as e:
        logger.error(f"AI Insights error: {e}")
        return {
            "resumen_reviews": "Servicio de análisis temporalmente no disponible.",
            "sugerencia_produccion": "Mantener niveles de stock base."
        }

@router.post("/abrir-cajon")
async def abrir_cajon_remoto(db: Session = Depends(get_db)):
    """Comando remoto para apertura física de cajón de monedas."""
    cmd = HardwareCommand(
        id=str(uuid.uuid4()),
        accion="abrir_caja",
        origen="dashboard_remoto_admin"
    )
    db.add(cmd)
    db.commit()
    logger.warning("SOLICITUD DE APERTURA DE CAJÓN REMOTA REGISTRADA")
    return {"status": "command_queued"}
