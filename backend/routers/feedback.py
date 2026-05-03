from fastapi import APIRouter
from pydantic import BaseModel, Field
import uuid
import datetime

router = APIRouter(prefix="/feedback", tags=["Customer Experience & NPS"])

class FeedbackCreate(BaseModel):
    order_id: str
    calificacion: int = Field(..., ge=1, le=5)
    comentario: str = ""
    recomendaria: bool = True

class FeedbackOut(FeedbackCreate):
    id: str
    fecha: datetime.datetime

# Base de datos en memoria para el prototipo industrializado
FEEDBACK_DB = []

@router.post("/", response_model=FeedbackOut)
def enviar_feedback(fb: FeedbackCreate):
    """
    Fase 29: Recolección de Feedback post-venta.
    Permite medir el NPS (Net Promoter Score) de la Experiencia Gourmet.
    """
    nuevo = FeedbackOut(
        id=str(uuid.uuid4()),
        fecha=datetime.datetime.now(),
        **fb.dict()
    )
    FEEDBACK_DB.append(nuevo)
    return nuevo

@router.get("/metrics")
def get_nps_metrics():
    """Cálculo automático del índice de satisfacción del cliente."""
    if not FEEDBACK_DB:
        return {"nps": 0, "satisfaccion_media": 0, "total_opiniones": 0}
        
    promotores = len([f for f in FEEDBACK_DB if f.calificacion >= 4])
    total = len(FEEDBACK_DB)
    score = (promotores / total) * 100
    
    return {
        "nps": round(score, 1),
        "satisfaccion_media": round(sum(f.calificacion for f in FEEDBACK_DB) / total, 2),
        "total_opiniones": total
    }
