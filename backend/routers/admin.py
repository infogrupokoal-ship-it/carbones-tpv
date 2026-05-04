import uuid
import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field

from ..database import get_db
from ..models import Producto, Pedido, ItemPedido, Review, ReporteZ, HardwareCommand, Categoria, Usuario, TareaOperativa
from ..ai_agent import ask_asador_ai
from ..utils.logger import logger
from scripts.seed_ultra import seed_ultra_industrial
from .admin_audit import log_audit_action
from .dependencies import require_admin, get_current_user

router = APIRouter(prefix="/admin", tags=["Gestión Administrativa"], dependencies=[Depends(require_admin)])

# --- Esquemas de Datos ---

class TareaCreate(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=100)
    descripcion: Optional[str] = None
    prioridad: str = "MEDIA" # BAJA, MEDIA, ALTA, CRITICA

class TareaUpdate(BaseModel):
    estado: str # PENDIENTE, COMPLETADO

class ProductoCreate(BaseModel):
    nombre: str = Field(..., json_schema_extra={"example": "Pollo Asado XL"})
    precio: float = Field(..., gt=0, json_schema_extra={"example": 12.50})
    categoria_id: str = Field(..., json_schema_extra={"example": "cat-pollos"})
    stock_actual: float = Field(0, ge=0)

class CierreRequest(BaseModel):
    efectivo_declarado: Optional[float] = Field(None, ge=0, json_schema_extra={"example": 150.00})

class KPIOut(BaseModel):
    ventas_hoy: float
    coste_mermas: float
    pedidos_b2c: int
    pedidos_domicilio: int
    avg_rating: float

class DashboardOut(BaseModel):
    kpis: KPIOut
    charts: Dict[str, Any]
    reviews: List[Dict[str, Any]]

# --- Endpoints Administrativos ---

@router.get("/status", tags=["Gestión Administrativa"])
async def get_admin_status():
    return {"status": "authorized", "engine": "Enterprise-v5.0"}

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
            "resumen_reviews": resumen.replace("AI:", "").strip(),
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
    Agente Conversacional: Proporciona soporte operativo e insights 
    estratégicos mediante interacción en lenguaje natural.
    """
    try:
        message = data.get("message", "")
        if not message:
            raise HTTPException(status_code=400, detail="Mensaje vacío")
            
        # Contexto del sistema para el agente
        prompt = f"El usuario pregunta: {message}\nResponde como el asistente experto del TPV Carbones y Pollos."
        response = await ask_asador_ai(prompt, user_role="staff")
        return {"response": response.replace("AI:", "").strip()}
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
        
        # Auditoría Industrial
        log_audit_action(
            db=db,
            usuario_id=None,
            accion="SEED_PRODUCTION_DATA",
            entidad="SISTEMA",
            payload_nuevo="Ejecución de seeding ultra industrial premium."
        )
        
        return {"status": "success", "message": "Ecosistema de datos Ultra-Premium inicializado."}
    except Exception as e:
        logger.error(f"Fallo en Seeding: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/factory_reset", status_code=status.HTTP_200_OK)
async def factory_reset(db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):
    """
    Comando de Emergencia: Limpia todo el catálogo y pedidos para un despliegue limpio.
    ¡USAR CON PRECAUCIÓN!
    """
    try:
        db.query(ItemPedido).delete()
        db.query(Pedido).delete()
        db.query(Producto).delete()
        db.query(Categoria).delete()
        
        # Auditoría Industrial
        log_audit_action(
            db=db,
            usuario_id=current_user.id,
            accion="FACTORY_RESET",
            entidad="SISTEMA",
            payload_nuevo="Reseteo completo de tablas transaccionales y catálogo."
        )
        
        db.commit()
        return {"status": "success", "message": "Sistema reseteado a valores de fábrica."}
    except Exception as e:
        db.rollback()
        raise HTTPException(500, detail=str(e))

@router.post("/abrir-cajon", status_code=status.HTTP_202_ACCEPTED)
async def abrir_cajon_remoto(db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):
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
    
    # Auditoría Industrial
    log_audit_action(
        db=db,
        usuario_id=current_user.id,
        accion="ABRIR_CAJON_REMOTO",
        entidad="HARDWARE",
        payload_nuevo=f"Solicitud remota de apertura de caja por {current_user.username}."
    )
    
    db.commit()
    logger.warning(f"AUDITORÍA: Apertura de cajón solicitada remotamente por {current_user.username}.")
    return {"status": "success", "detail": "Comando de apertura encolado"}

@router.get("/dashboard/kpis", response_model=DashboardOut)
async def get_dashboard_kpis(db: Session = Depends(get_db)):
    """
    Motor de Inteligencia de Negocio: Agrega métricas críticas de la jornada.
    """
    hoy = datetime.date.today().strftime("%Y-%m-%d")
    
    try:
        # KPIs
        ventas_hoy = db.query(func.sum(Pedido.total)).filter(func.date(Pedido.fecha) == hoy).scalar() or 0.0
        coste_mermas = db.query(func.sum(ReporteZ.coste_mermas)).filter(func.date(ReporteZ.fecha) == hoy).scalar() or 0.0
        pedidos_b2c = db.query(Pedido).filter(func.date(Pedido.fecha) == hoy).count()
        pedidos_domicilio = db.query(Pedido).filter(func.date(Pedido.fecha) == hoy, Pedido.metodo_envio == "DOMICILIO").count()
        avg_rating = db.query(func.avg(Review.rating)).scalar() or 0.0
        
        kpis = KPIOut(
            ventas_hoy=float(ventas_hoy),
            coste_mermas=float(coste_mermas),
            pedidos_b2c=pedidos_b2c,
            pedidos_domicilio=pedidos_domicilio,
            avg_rating=round(float(avg_rating), 1)
        )
        
        # Real Data for Charts
        # 1. Ventas Semanales (Últimos 7 días)
        fecha_inicio = datetime.date.today() - datetime.timedelta(days=6)
        ventas_diarias = db.query(
            func.date(Pedido.fecha).label('dia'),
            func.sum(Pedido.total).label('total')
        ).filter(Pedido.fecha >= fecha_inicio).group_by('dia').order_by('dia').all()
        
        # Mapear ventas diarias, rellenando días sin ventas con 0
        ventas_dict = {str(v.dia): float(v.total) for v in ventas_diarias}
        ventas_semanales = []
        dias_semana = []
        for i in range(7):
            dia_actual = fecha_inicio + datetime.timedelta(days=i)
            str_dia = str(dia_actual)
            ventas_semanales.append(ventas_dict.get(str_dia, 0.0))
            dias_semana.append(dia_actual.strftime("%a"))
            
        # 2. Categorías Top
        from sqlalchemy import desc
        top_categorias = db.query(
            Categoria.nombre,
            func.count(ItemPedido.id).label('cantidad')
        ).select_from(ItemPedido).join(Producto, ItemPedido.producto_id == Producto.id)\
         .join(Categoria, Producto.categoria_id == Categoria.id)\
         .group_by(Categoria.id).order_by(desc('cantidad')).limit(4).all()
        
        categorias_nombres = [c.nombre for c in top_categorias] if top_categorias else ["Pollos", "Pizzas", "Bebidas", "Complementos"]
        
        charts = {
            "ventas_semanales": ventas_semanales if sum(ventas_semanales) > 0 else [0]*7,
            "dias_semana": dias_semana,
            "categorias_top": categorias_nombres
        }
        
        # Reviews recientes
        recent_reviews = db.query(Review).order_by(Review.fecha.desc()).limit(5).all()
        reviews_list = [
            {"rating": r.rating, "comentario": r.comentario, "fecha": r.fecha.isoformat()} 
            for r in recent_reviews
        ]
        
        return DashboardOut(
            kpis=kpis,
            charts=charts,
            reviews=reviews_list
        )
    except Exception as e:
        logger.error(f"Error en Dashboard KPIs: {e}")
        # Fallback para no bloquear la UI
        return DashboardOut(
            kpis=KPIOut(ventas_hoy=0, coste_mermas=0, pedidos_b2c=0, pedidos_domicilio=0, avg_rating=0),
            charts={},
            reviews=[]
        )

# --- Gestión de Tareas Operativas ---

@router.get("/tasks", response_model=List[Dict[str, Any]])
async def list_tasks(db: Session = Depends(get_db)):
    tasks = db.query(TareaOperativa).order_by(TareaOperativa.fecha.desc()).limit(50).all()
    return [
        {
            "id": t.id,
            "fecha": t.fecha.isoformat(),
            "titulo": t.titulo,
            "descripcion": t.descripcion,
            "prioridad": t.prioridad,
            "estado": t.estado
        } for t in tasks
    ]

@router.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(tarea: TareaCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    # Obtener tienda_id del usuario o tienda central por defecto
    tienda_id = current_user.tienda_id if current_user else db.query(Usuario).first().tienda_id
    
    new_task = TareaOperativa(
        id=str(uuid.uuid4()),
        titulo=tarea.titulo,
        descripcion=tarea.descripcion,
        prioridad=tarea.prioridad,
        estado="PENDIENTE",
        usuario_id=current_user.id if current_user else None,
        tienda_id=tienda_id
    )
    db.add(new_task)
    
    log_audit_action(
        db=db,
        usuario_id=current_user.id if current_user else None,
        accion="CREATE_TASK",
        entidad="TAREA_OPERATIVA",
        payload_nuevo=f"Nueva tarea: {tarea.titulo} ({tarea.prioridad})"
    )
    
    db.commit()
    return {"status": "success", "id": new_task.id}

@router.patch("/tasks/{task_id}")
async def update_task_status(task_id: str, update: TareaUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    task = db.query(TareaOperativa).filter(TareaOperativa.id == task_id).first()
    if not task:
        raise HTTPException(404, detail="Tarea no encontrada")
    
    old_status = task.estado
    task.estado = update.estado
    
    log_audit_action(
        db=db,
        usuario_id=current_user.id if current_user else None,
        accion="UPDATE_TASK_STATUS",
        entidad="TAREA_OPERATIVA",
        payload_previo=f"Estado: {old_status}",
        payload_nuevo=f"Estado: {update.estado}"
    )
    
    db.commit()
    return {"status": "success"}
