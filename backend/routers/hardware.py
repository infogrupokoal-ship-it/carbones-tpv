import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import HardwareCommand, Usuario
from .dependencies import require_admin

router = APIRouter(prefix="/hardware", tags=["Hardware"])


@router.get("/poll")
def poll_commands(db: Session = Depends(get_db)):
    """
    Endpoint utilizado por el local_printer_bridge para obtener
    comandos pendientes (impresión, apertura de caja).
    """
    comandos = (
        db.query(HardwareCommand).filter(HardwareCommand.estado == "PENDIENTE").all()
    )

    return {"comandos": comandos}


@router.post("/ack/{command_id}")
def acknowledge_command(command_id: str, db: Session = Depends(get_db)):
    """Marca un comando como ejecutado."""
    cmd = db.query(HardwareCommand).filter(HardwareCommand.id == command_id).first()
    if not cmd:
        raise HTTPException(status_code=404, detail="Comando no encontrado")

    cmd.estado = "EJECUTADO"
    cmd.procesado = True
    cmd.fecha_ejecucion = datetime.now()
    db.commit()
    return {"status": "ok"}


@router.post("/abrir_caja")
def push_abrir_caja(origen: str = "ADMIN_API", db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):
    """Encola un comando para abrir el cajón portamonedas."""
    nuevo_cmd = HardwareCommand(
        id=str(uuid.uuid4()), accion="abrir_caja", origen=origen
    )
    db.add(nuevo_cmd)
    db.commit()
    return {"status": "ok", "command_id": nuevo_cmd.id}
