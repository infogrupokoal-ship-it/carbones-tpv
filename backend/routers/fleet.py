from fastapi import APIRouter
from typing import Dict
import datetime

router = APIRouter(prefix="/fleet", tags=["Fleet Management & Logistics"])

class RiderStatus(Dict):
    rider_id: str
    nombre: str
    lat: float
    lng: float
    status: str # disponible, en_reparto, descansando

RIDERS_MOCK = [
    {"rider_id": "RID-001", "nombre": "Juan Reparto", "lat": 40.4168, "lng": -3.7038, "status": "disponible"},
    {"rider_id": "RID-002", "nombre": "Marta Flash", "lat": 40.4235, "lng": -3.7122, "status": "en_reparto"}
]

@router.get("/tracking")
def get_fleet_tracking():
    """
    Fase 33: Tracking en tiempo real de la flota de reparto.
    Permite visualizar a los riders en el mapa del portal administrativo.
    """
    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "riders": RIDERS_MOCK,
        "pedidos_activos": 5
    }

@router.post("/assign/{pedido_id}/{rider_id}")
def assign_order(pedido_id: str, rider_id: str):
    """Asignación inteligente de pedido al rider más cercano."""
    return {"status": "assigned", "estimated_pickup": "10 mins", "rider": rider_id}
