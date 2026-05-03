from fastapi import APIRouter, Depends
from backend.routers.auth import get_current_user, require_admin
from backend.models import Usuario
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
    scope: str = "ADMIN" # ADMIN, MANAGER, ALL

# In-memory store (simulation)
NOTIFICATIONS_STORE = [
    {
        "id": str(uuid.uuid4()),
        "title": "Bienvenido al Sistema",
        "message": "Protocolo Quantum Singularity V6 activo.",
        "type": "info",
        "timestamp": datetime.now(),
        "module": "System",
        "scope": "ALL"
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Rotura de Stock Detectada",
        "message": "El stock de 'Pollo de Corral' está por debajo del 10%.",
        "type": "warning",
        "timestamp": datetime.now(),
        "module": "Inventario",
        "scope": "MANAGER"
    }
]

@router.get("/", response_model=List[Notification])
def get_notifications(current_user: Usuario = Depends(get_current_user)):
    """
    Retorna notificaciones filtradas por el rol del usuario.
    Un usuario normal (CASHIER) solo verá notificaciones de alcance 'ALL'.
    Un MANAGER verá 'ALL' y 'MANAGER'.
    Un ADMIN verá todas.
    """
    user_role = current_user.rol
    
    filtered = []
    for n in NOTIFICATIONS_STORE:
        scope = n.get("scope", "ADMIN")
        if user_role == "ADMIN":
            filtered.append(n)
        elif user_role == "MANAGER" and scope in ["MANAGER", "ALL"]:
            filtered.append(n)
        elif scope == "ALL":
            filtered.append(n)
            
    return filtered

@router.post("/", dependencies=[Depends(require_admin)])
def create_notification(notif: Notification):
    """Solo los administradores o servicios internos pueden crear notificaciones."""
    NOTIFICATIONS_STORE.insert(0, notif.dict())
    return {"status": "ok"}
