from fastapi import APIRouter
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/loyalty", tags=["Advanced Loyalty & Gamification"])

class RewardTier(BaseModel):
    name: str
    min_points: int
    benefit: str

LOYALTY_TIERS = [
    RewardTier(name="BRONZE", min_points=0, benefit="5% Dto. en Martes"),
    RewardTier(name="SILVER", min_points=500, benefit="1 Pollo gratis al mes"),
    RewardTier(name="GOLD", min_points=2000, benefit="Acceso prioritario y 15% Dto. total"),
]

@router.get("/tiers")
def get_tiers():
    """Fase 35: Motor de Gamificación. Define los niveles de recompensa para clientes VIP."""
    return LOYALTY_TIERS

@router.post("/earn-points")
def earn_points(cliente_id: str, total_pedido: float):
    """Calcula y asigna puntos basados en el consumo (1 EUR = 10 Puntos)."""
    puntos_ganados = int(total_pedido * 10)
    return {
        "cliente_id": cliente_id,
        "puntos_ganados": puntos_ganados,
        "nuevo_saldo": 1250, # Mock
        "proximo_tier": "GOLD",
        "puntos_faltantes": 750
    }
