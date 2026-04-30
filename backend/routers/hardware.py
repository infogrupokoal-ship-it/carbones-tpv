from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import uuid

from ..database import get_db
from ..models import HardwareCommand
from ..utils.db_logger import DBLogger
from pydantic import BaseModel

router = APIRouter(prefix="/hardware", tags=["Infraestructura de Hardware"])

class CommandCreate(BaseModel):
    accion: str
    payload: str = None
    origen: str = "app_master"

@router.get("/pending")
def get_pending_commands(db: Session = Depends(get_db)):
    """Consulta comandos pendientes para el puente físico."""
    commands = db.query(HardwareCommand).filter(HardwareCommand.estado == "PENDIENTE").all()
    return commands

@router.post("/confirm/{command_id}")
def confirm_command_execution(command_id: str, db: Session = Depends(get_db)):
    """Confirma que el comando físico ha sido ejecutado con éxito."""
    cmd = db.query(HardwareCommand).filter(HardwareCommand.id == command_id).first()
    if not cmd:
        raise HTTPException(status_code=404, detail="Comando no encontrado")
    
    cmd.estado = "EJECUTADO"
    cmd.fecha_ejecucion = datetime.now()
    db.commit()
    
    DBLogger.info("HARDWARE", f"Comando {cmd.accion} confirmado y ejecutado.")
    return {"status": "confirmed"}

@router.post("/enqueue")
def enqueue_command(cmd_data: CommandCreate, db: Session = Depends(get_db)):
    """Añade un comando a la cola de hardware (Ej: Abrir caja desde móvil)."""
    nuevo_cmd = HardwareCommand(
        id=str(uuid.uuid4()),
        accion=cmd_data.accion,
        payload=cmd_data.payload,
        origen=cmd_data.origen,
        estado="PENDIENTE"
    )
    db.add(nuevo_cmd)
    db.commit()
    return {"status": "enqueued", "id": nuevo_cmd.id}
