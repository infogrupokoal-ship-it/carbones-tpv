from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Cliente
from ..utils.logger import logger

router = APIRouter(prefix="/loyalty", tags=["Loyalty & Gamification"])

class RewardTier(BaseModel):
    name: str
    min_points: int
    benefit: str

LOYALTY_TIERS = [
    RewardTier(name="BRONCE", min_points=0, benefit="5% Dto. en Martes"),
    RewardTier(name="PLATA", min_points=500, benefit="1 Pollo gratis al mes"),
    RewardTier(name="ORO", min_points=2000, benefit="Acceso prioritario y 15% Dto. total"),
]

@router.get("/tiers")
def get_tiers():
    """Define los niveles de recompensa para clientes VIP."""
    return LOYALTY_TIERS

@router.post("/earn-points")
def earn_points(cliente_id: str, total_pedido: float, db: Session = Depends(get_db)):
    """Calcula y asigna puntos basados en el consumo (1 EUR = 10 Puntos)."""
    try:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        puntos_ganados = int(total_pedido * 10)
        cliente.puntos_fidelidad = (cliente.puntos_fidelidad or 0) + puntos_ganados
        
        # Actualizar nivel
        nuevo_nivel = "BRONCE"
        for tier in sorted(LOYALTY_TIERS, key=lambda x: x.min_points, reverse=True):
            if cliente.puntos_fidelidad >= tier.min_points:
                nuevo_nivel = tier.name
                break
        
        cliente.nivel_fidelidad = nuevo_nivel
        db.commit()
        
        return {
            "cliente_id": cliente_id,
            "puntos_ganados": puntos_ganados,
            "nuevo_saldo": cliente.puntos_fidelidad,
            "nivel_actual": cliente.nivel_fidelidad
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error asignando puntos de fidelidad: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/customer/{cliente_id}")
def get_customer_loyalty(cliente_id: str, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    return {
        "puntos": cliente.puntos_fidelidad or 0,
        "nivel": cliente.nivel_fidelidad or "BRONCE",
        "visitas": cliente.visitas or 0
    }
