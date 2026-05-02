from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

router = APIRouter(prefix="/notifications", tags=["Notifications"])

class Notification(BaseModel):
    id: str
    title: str
    message: str
    type: str # info, success, warning, error
    timestamp: datetime
    module: Optional[str] = "Global"

# In-memory store for demo (should be DB in production)
NOTIFICATIONS_STORE = [
    {
        "id": str(uuid.uuid4()),
        "title": "Rotura de Stock Detectada",
        "message": "El stock de 'Pollo de Corral' está por debajo del 10%.",
        "type": "warning",
        "timestamp": datetime.now(),
        "module": "Inventario"
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Nuevo Pedido Online",
        "message": "Se ha recibido un pedido de 45.50€ vía UberEats.",
        "type": "success",
        "timestamp": datetime.now(),
        "module": "Caja"
    }
]

@router.get("/", response_model=List[Notification])
def get_notifications():
    return NOTIFICATIONS_STORE

@router.post("/")
def create_notification(notif: Notification):
    NOTIFICATIONS_STORE.insert(0, notif.dict())
    return {"status": "ok"}
