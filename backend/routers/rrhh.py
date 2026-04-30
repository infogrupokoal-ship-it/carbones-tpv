from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from ..database import get_db
from ..models import Usuario, Fichaje
from ..utils.logger import logger
from ..utils.auth import verify_password

router = APIRouter(prefix="/rrhh", tags=["Recursos Humanos"])

# --- Esquemas ---
class FichajeRequest(BaseModel):
    pin: str
    tipo: str  # ENTRADA, SALIDA, INICIO_PAUSA, FIN_PAUSA

class FichajeResponse(BaseModel):
    username: str
    tipo: str
    fecha: str

# --- Endpoints ---

@router.post("/fichar")
async def registrar_fichaje(req: FichajeRequest, db: Session = Depends(get_db)):
    """Registra un evento de fichaje validando el PIN del usuario."""
    
    users = db.query(Usuario).filter(Usuario.is_active == True).all()
    user = next((u for u in users if verify_password(req.pin, u.pin_hash)), None)
    
    if not user:
        logger.warning(f"Intento de fichaje con PIN inválido: ***{req.pin[-1]}")
        raise HTTPException(status_code=401, detail="PIN incorrecto")
    
    nuevo_fichaje = Fichaje(
        usuario_id=user.id,
        tipo=req.tipo,
        fecha=datetime.now()
    )
    db.add(nuevo_fichaje)
    db.commit()
    
    logger.info(f"Fichaje registrado: {user.username} - {req.tipo}")
    
    return {
        "status": "success",
        "msj": f"¡Hola {user.username}! {req.tipo} registrado correctamente.",
        "username": user.username
    }

@router.get("/fichajes", response_model=List[FichajeResponse])
async def obtener_fichajes_recientes(limit: int = 10, db: Session = Depends(get_db)):
    """Lista los últimos fichajes realizados en el sistema."""
    fichajes = db.query(Fichaje).order_by(desc(Fichaje.fecha)).limit(limit).all()
    
    return [
        FichajeResponse(
            username=f.usuario.username if f.usuario else "Desconocido",
            tipo=f.tipo,
            fecha=f.fecha.strftime("%d/%m %H:%M") if f.fecha else "--"
        ) for f in fichajes
    ]

@router.get("/dashboard/stats")
async def get_hr_stats(db: Session = Depends(get_db)):
    """Estadísticas rápidas para el dashboard de RRHH."""
    today = datetime.now().date()
    empleados_activos = db.query(Usuario).filter(Usuario.is_active == True).count()
    fichajes_hoy = db.query(Fichaje).filter(func.date(Fichaje.fecha) == today).count()
    
    return {
        "empleados_totales": empleados_activos,
        "fichajes_hoy": fichajes_hoy,
        "puesto_critico": "Cocina" # Placeholder inteligente
    }
