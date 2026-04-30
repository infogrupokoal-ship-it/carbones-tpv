import uuid
import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Producto, Pedido
from ..services.financials import FinancialService
from ..ai_agent import ask_asador_ai
from ..utils.logger import logger
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["Gestión Administrativa"])
router_legacy = APIRouter(prefix="/config", tags=["Soporte Legacy"], include_in_schema=False)

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
    """Métricas integrales para el Dashboard de Control Directivo."""
    today = datetime.date.today()
    
    # KPIs de Ventas
    ventas_hoy = db.query(func.sum(Pedido.total)).filter(func.date(Pedido.fecha) == today).scalar() or 0.0
    pedidos_count = db.query(Pedido).filter(func.date(Pedido.fecha) == today).count()
    
    # Análisis de Tendencia (Mock para visualización)
    charts = {
        "horas": {
            "labels": ["10:00", "12:00", "14:00", "16:00", "18:00", "20:00", "22:00"],
            "data": [10, 45, 120, 30, 15, 80, 50]
        }
    }
    
    return {
        "kpis": {
            "ventas_hoy": round(ventas_hoy, 2),
            "pedidos_b2c": pedidos_count,
            "status": "online"
        },
        "charts": charts
    }

@router.post("/cierre-z")
async def ejecutar_cierre_z(data: CierreRequest, db: Session = Depends(get_db)):
    """
    Ejecuta el cierre de caja oficial. 
    Consolida ventas, purga inventario perecedero y genera el reporte financiero.
    """
    try:
        mensaje = FinancialService.generate_z_report(db, data.efectivo_declarado)
        
        # Enviar por WhatsApp si el servicio está configurado
        # (Lógica delegada a un worker de background en una implementación real completa)
        
        return {"status": "success", "report": mensaje}
    except Exception as e:
        logger.error(f"Error en Cierre Z: {e}")
        raise HTTPException(status_code=500, detail="Fallo en la ejecución del cierre financiero.")

@router.post("/abrir-cajon")
async def abrir_cajon_remoto():
    """Comando remoto para apertura física de cajón de monedas."""
    # Aquí se enviaría el comando a la hardware bridge local
    logger.warning("SOLICITUD DE APERTURA DE CAJÓN REMOTA RECIBIDA")
    return {"status": "command_sent"}

@router.post("/ai/chat")
async def admin_ai_chat(data: dict):
    """Interfaz conversacional con el analista estratégico Koal-AI."""
    message = data.get("message", "")
    if not message:
        raise HTTPException(status_code=400, detail="Mensaje vacío")
        
    response_text = await ask_asador_ai(message, user_role="admin")
    return {"response": response_text}

# --- Registro de Productos y Catálogo ---

@router.post("/productos", response_model=dict)
def crear_producto(prod: ProductoCreate, db: Session = Depends(get_db)):
    nuevo = Producto(
        id=str(uuid.uuid4()),
        nombre=prod.nombre,
        precio=prod.precio,
        categoria_id=prod.categoria_id,
        stock_actual=prod.stock_actual
    )
    db.add(nuevo)
    db.commit()
    logger.info(f"Nuevo producto creado: {prod.nombre}")
    return {"id": nuevo.id}

@router.get("/summary")
@router_legacy.get("/resumen")
def get_legacy_summary(db: Session = Depends(get_db)):
    """Endpoint de compatibilidad para herramientas externas antiguas."""
    ventas = db.query(func.sum(Pedido.total)).scalar() or 0.0
    return {
        "ventas_totales": round(ventas, 2),
        "total_pedidos": db.query(Pedido).count()
    }
