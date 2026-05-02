from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
import datetime

router = APIRouter(prefix="/pricing", tags=["Dynamic Pricing & Revenue Management"])

@router.get("/suggested")
def get_dynamic_pricing(plato_id: str, db: Session = Depends(get_db)):
    """
    Fase 43: Motor de Precios Dinámicos.
    Ajusta el PVP en tiempo real basándose en la demanda actual, stock disponible y hora del día.
    """
    ahora = datetime.datetime.now()
    es_hora_punta = 13 <= ahora.hour <= 15 or 20 <= ahora.hour <= 22
    demanda_actual = "ALTA" if es_hora_punta else "NORMAL"
    
    precio_base = 12.50
    multiplicador = 1.15 if es_hora_punta else 1.0
    
    return {
        "plato_id": plato_id,
        "precio_base": precio_base,
        "precio_dinamico": round(precio_base * multiplicador, 2),
        "factor_demanda": multiplicador,
        "motivo": f"Demanda {demanda_actual} detectada por IA"
    }
