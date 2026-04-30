from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Usuario  # Asumiendo que Usuario tiene los campos necesarios o crearemos Shift

router = APIRouter(prefix="/rrhh", tags=["Recursos Humanos"])
router_legacy = APIRouter(prefix="/personal", tags=["Legacy Personal"])

# --- Esquemas Pydantic ---
class ShiftIn(BaseModel):
    usuario_id: str
    accion: str  # "ENTRADA", "SALIDA"

class UserStats(BaseModel):
    username: str
    total_pedidos: int
    total_recaudado: float

# NOTA: Para una implementación real de RRHH, deberíamos tener una tabla 'Shifts' o 'Fichajes'.
# Por ahora, implementaremos la lógica básica de control de presencia.

@router.post("/fichar")
@router_legacy.post("/fichar")
def registrar_fichaje(req: ShiftIn, db: Session = Depends(get_db)):
    """Registra la entrada o salida de un empleado."""
    user = db.query(Usuario).get(req.usuario_id)
    if not user:
        raise HTTPException(404, "Empleado no encontrado")
    
    # En un sistema profesional, esto guardaría en una tabla 'asistencia'
    # Por ahora simulamos el log
    print(f"-> [RRHH] {user.username} ha registrado: {req.accion} a las {datetime.now()}")
    
    return {"status": "ok", "empleado": user.username, "accion": req.accion, "hora": datetime.now().isoformat()}

@router.get("/dashboard")
def stats_personal(db: Session = Depends(get_db)):
    """Obtiene estadísticas de rendimiento del personal."""
    # Simulación de datos para el dashboard profesional
    usuarios = db.query(Usuario).all()
    stats = []
    for u in usuarios:
        stats.append({
            "id": u.id,
            "username": u.username,
            "rol": u.rol,
            "ventas_hoy": 150.0, # Placeholder
            "pedidos_hoy": 12,    # Placeholder
            "estado": "ACTIVO"
        })
    return stats
