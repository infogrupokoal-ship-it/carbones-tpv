import uuid
import datetime
import json
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field

from ..database import get_db
from ..models import Producto, Pedido, ItemPedido, MovimientoStock, Review, Usuario, ReporteZ, HardwareCommand
from ..services.reporting import ReportingService
from ..ai_agent import ask_asador_ai
from ..utils.logger import logger
from scripts.seed_ultra import seed_ultra_industrial

router = APIRouter(prefix="/admin", tags=["Gestión Administrativa"])

# --- Esquemas de Datos ---

class ProductoCreate(BaseModel):
    nombre: str = Field(..., example="Pollo Asado XL")
    precio: float = Field(..., gt=0, example=12.50)
    categoria_id: str = Field(..., example="cat-pollos")
    stock_actual: float = Field(0, ge=0)

class CierreRequest(BaseModel):
    efectivo_declarado: Optional[float] = Field(None, ge=0, example=150.00)

class KPIOut(BaseModel):
    ventas_hoy: float
    coste_mermas: float
    pedidos_b2c: int
    avg_rating: float

class DashboardOut(BaseModel):
    kpis: KPIOut
    charts: Dict[str, Any]
    reviews: List[Dict[str, Any]]

# --- Endpoints Administrativos ---

@router.get("/dashboard/kpis", response_model=DashboardOut)
async def get_dashboard_kpis(db: Session = Depends(get_db)):
    """
    Motor de inteligencia de negocio: Calcula métricas operativas, 
    tendencias de ventas y satisfacción del cliente en tiempo real.
    """
    try:
        today = datetime.date.today()
        
        # 1. KPIs principales
        ventas_hoy = db.query(func.sum(Pedido.total)).filter(func.date(Pedido.fecha) == today).scalar() or 0.0
        pedidos_count = db.query(Pedido).filter(func.date(Pedido.fecha) == today).count()
        
        # Coste estimado de mermas (Sobrantes de hoy con valoración al 40% del PVP)
        mermas_hoy = db.query(func.sum(MovimientoStock.cantidad * Producto.precio * 0.4))\
            .join(Producto)\
            .filter(MovimientoStock.tipo == "SOBRANTE_DIA")\
            .filter(func.date(MovimientoStock.fecha) == today).scalar() or 0.0
            
        avg_rating = db.query(func.avg(Review.rating)).scalar() or 5.0

        # 2. Análisis Temporal de Ventas
        ventas_por_hora = db.query(
            func.strftime("%H:00", Pedido.fecha).label("hora"),
            func.sum(Pedido.total).label("total")
        ).filter(func.date(Pedido.fecha) == today)\
         .group_by("hora").order_by("hora").all()

        # 3. Rendimiento por Categoría (Top 5)
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

        # 4. Auditoría de Satisfacción
        recent_reviews = db.query(Review).order_by(Review.fecha.desc()).limit(5).all()
        reviews_data = [{
            "rating": r.rating,
            "comentario": r.comentario,
            "fecha": r.fecha.strftime("%H:%M") if r.fecha else "--:--",
            "cliente_nombre": "Cliente TPV"
        } for r in recent_reviews]

        return DashboardOut(
            kpis=KPIOut(
                ventas_hoy=round(ventas_hoy, 2),
                coste_mermas=round(abs(mermas_hoy), 2),
                pedidos_b2c=pedidos_count,
                avg_rating=round(float(avg_rating), 1)
            ),
            charts={
                "horas": {
                    "labels": [v[0] for v in ventas_por_hora] if ventas_por_hora else ["Esperando datos..."],
                    "data": [v[1] for v in ventas_por_hora] if ventas_por_hora else [0]
                },
                "pollos": {
                    "labels": [v[0] for v in top_pollos],
                    "data": [float(v[1]) for v in top_pollos]
                },
                "pizzas": {
                    "labels": [v[0] for v in top_pizzas],
                    "data": [float(v[1]) for v in top_pizzas]
                }
            },
            reviews=reviews_data
        )
    except Exception as e:
        logger.error(f"Error en KPIs de Dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al generar métricas de negocio")

@router.post("/trigger_cierre_z", status_code=status.HTTP_201_CREATED)
async def trigger_cierre_z(data: CierreRequest, db: Session = Depends(get_db)):
    """
    Ejecuta el Cierre Z oficial de la jornada, consolidando datos fiscales
    y notificando a gerencia mediante canales automáticos.
    """
    try:
        reporte = ReportingService.generar_cierre_z(db, data.efectivo_declarado)
        logger.info(f"Cierre Z Generado: ID {reporte.id} | Total: {reporte.total_ventas}€")
        return {
            "status": "success", 
            "message": "Cierre Z consolidado correctamente", 
            "report_id": reporte.id
        }
    except Exception as e:
        logger.error(f"Fallo crítico en Cierre Z: {e}")
        raise HTTPException(status_code=500, detail="Error en la consolidación fiscal del cierre")

@router.get("/ai_insights")
async def get_ai_insights(db: Session = Depends(get_db)):
    """
    Servicio de Consultoría IA: Analiza el pulso del negocio mediante el procesamiento
    de lenguaje natural de las reseñas y el histórico de ventas.
    """
    try:
        ventas_hoy = db.query(func.sum(Pedido.total)).filter(func.date(Pedido.fecha) == datetime.date.today()).scalar() or 0.0
        reviews = db.query(Review).order_by(Review.fecha.desc()).limit(10).all()
        review_texts = "\n".join([f"- {r.rating}*: {r.comentario}" for r in reviews])
        
        prompt = f"""
        Como consultor experto en hostelería, analiza estos datos de hoy:
        - Facturación Bruta: {ventas_hoy}€
        - Feedback de clientes:
        {review_texts if review_texts else "Sin comentarios nuevos."}
        
        OBJETIVO:
        1. Resume el sentimiento del cliente en una frase potente.
        2. Proporciona una acción operativa concreta para mejorar el margen o el servicio mañana.
        """
        
        response = await ask_asador_ai(prompt, user_role="analyst")
        
        # Procesamiento elegante de la respuesta
        parts = response.split("\n\n")
        resumen = parts[0] if len(parts) > 0 else "Operativa estable con tendencia positiva."
        sugerencia = parts[1] if len(parts) > 1 else "Mantener niveles de producción según demanda histórica."
        
        return {
            "resumen_reviews": resumen.replace("Koal-AI:", "").strip(),
            "sugerencia_produccion": sugerencia.strip()
        }
    except Exception as e:
        logger.error(f"Fallo en AI Insights: {e}")
        return {
            "resumen_reviews": "Servicio de análisis en mantenimiento preventivo.",
            "sugerencia_produccion": "Seguir protocolos estándar de operación."
        }

@router.post("/ai/chat")
async def ai_chat(data: Dict[str, str], db: Session = Depends(get_db)):
    """
    Agente Conversacional Koal-AI: Proporciona soporte operativo e insights 
    estratégicos mediante interacción en lenguaje natural.
    """
    try:
        message = data.get("message", "")
        if not message:
            raise HTTPException(status_code=400, detail="Mensaje vacío")
            
        # Contexto del sistema para el agente
        prompt = f"El usuario pregunta: {message}\nResponde como el asistente experto del TPV Carbones y Pollos."
        response = await ask_asador_ai(prompt, user_role="staff")
        return {"response": response.replace("Koal-AI:", "").strip()}
    except Exception as e:
        logger.error(f"Error en AI Chat: {e}")
        return {"response": "Lo siento, mi conexión con el núcleo neuronal está inestable. ¿Puedes repetir?"}

@router.post("/seed_production", status_code=status.HTTP_201_CREATED)
async def seed_production_data(db: Session = Depends(get_db)):
    """
    Motor de Industrialización: Inicializa el ecosistema con datos premium.
    Evita estados vacíos en producción garantizando un catálogo funcional.
    """
    try:
        # Ejecutamos la lógica centralizada del seeder ultra
        seed_ultra_industrial()
        return {"status": "success", "message": "Ecosistema de datos Ultra-Premium inicializado."}
    except Exception as e:
        logger.error(f"Fallo en Seeding: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/factory_reset", status_code=status.HTTP_200_OK)
async def factory_reset(db: Session = Depends(get_db)):
    """
    Comando de Emergencia: Limpia todo el catálogo y pedidos para un despliegue limpio.
    ¡USAR CON PRECAUCIÓN!
    """
    try:
        db.query(ItemPedido).delete()
        db.query(Pedido).delete()
        db.query(Producto).delete()
        db.query(Categoria).delete()
        db.commit()
        return {"status": "success", "message": "Sistema reseteado a valores de fábrica."}
    except Exception as e:
        db.rollback()
        raise HTTPException(500, detail=str(e))

@router.post("/abrir-cajon", status_code=status.HTTP_202_ACCEPTED)
async def abrir_cajon_remoto(db: Session = Depends(get_db)):
    """
    Comando de Seguridad: Solicita la apertura física del cajón portamonedas 
    desde el panel de administración central. Registra el evento para auditoría.
    """
    cmd = HardwareCommand(
        id=str(uuid.uuid4()),
        accion="abrir_caja",
        origen="admin_remote_dashboard"
    )
    db.add(cmd)
    db.commit()
    logger.warning("AUDITORÍA: Apertura de cajón solicitada remotamente por administrador.")
    return {"status": "success", "detail": "Comando de apertura encolado"}
