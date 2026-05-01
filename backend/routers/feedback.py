from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from ..database import get_db
from ..models import Review, Cliente
from ..utils.logger import logger

router = APIRouter(prefix="/feedback", tags=["Feedback"])

class ReviewCrear(BaseModel):
    rating: int
    comentario: str
    cliente_id: str | None = None

@router.post("/")
def crear_reseña(req: ReviewCrear, db: Session = Depends(get_db)):
    try:
        nueva_review = Review(
            id=str(uuid.uuid4()),
            rating=req.rating,
            comentario=req.comentario,
            cliente_id=req.cliente_id,
            fecha=datetime.utcnow()
        )
        db.add(nueva_review)
        db.commit()
        return {"status": "success", "message": "Gracias por tu opinión"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error creando reseña: {e}")
        raise HTTPException(status_code=500, detail="Error al guardar reseña")

@router.get("/latest")
def obtener_reseñas_recientes(db: Session = Depends(get_db)):
    reviews = db.query(Review).order_by(Review.fecha.desc()).limit(5).all()
    out = []
    for r in reviews:
        cliente = db.query(Cliente).get(r.cliente_id) if r.cliente_id else None
        out.append({
            "id": r.id,
            "rating": r.rating,
            "comentario": r.comentario,
            "cliente": cliente.nombre if cliente else "Invitado",
            "fecha": r.fecha.isoformat()
        })
    return out
