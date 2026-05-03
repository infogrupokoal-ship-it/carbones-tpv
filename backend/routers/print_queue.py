import uuid
import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import PrintJob, Usuario
from ..utils.logger import logger
from .dependencies import get_current_user, require_manager

router = APIRouter(prefix="/print/queue", tags=["Hardware"])

# --- Esquemas Pydantic ---

class PrintJobCreate(BaseModel):
    payload: str = Field(..., description="Contenido del ticket (JSON o Texto)")
    printer_type: str = Field("thermal", description="thermal, A4, label")
    target_device: Optional[str] = Field(None, description="ID del dispositivo destino")
    metadata_json: Optional[Dict[str, Any]] = None

class PrintJobOut(BaseModel):
    id: str
    created_at: datetime.datetime
    payload: str
    printer_type: str
    target_device: Optional[str]
    status: str
    attempts: int
    
    model_config = ConfigDict(from_attributes=True)

class PrintJobStatusUpdate(BaseModel):
    status: str # COMPLETED, FAILED, PENDING
    error_log: Optional[str] = None

# --- Rutas ---

@router.post("/", response_model=PrintJobOut, status_code=status.HTTP_201_CREATED)
def add_to_queue(job: PrintJobCreate, db: Session = Depends(get_db)):
    """
    Añade un nuevo trabajo a la cola de impresión industrial (Zero-Touch Architecture).
    """
    try:
        nuevo_job = PrintJob(
            id=str(uuid.uuid4()),
            payload=job.payload,
            printer_type=job.printer_type,
            target_device=job.target_device,
            metadata_json=job.metadata_json,
            status="PENDING"
        )
        db.add(nuevo_job)
        db.commit()
        db.refresh(nuevo_job)
        logger.info(f"[PRINT] Job encolado: {nuevo_job.id} para {job.target_device or 'todos'}")
        return nuevo_job
    except Exception as e:
        db.rollback()
        logger.error(f"Error añadiendo a cola de impresión: {e}")
        raise HTTPException(status_code=500, detail="Error al encolar trabajo de impresión")

@router.get("/pending", response_model=List[PrintJobOut])
def get_pending_jobs(target_device: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Recupera trabajos pendientes de impresión para un dispositivo específico o general (Poller).
    Automáticamente marca los trabajos como IN_FLIGHT para evitar colisiones.
    """
    try:
        # Recuperamos PENDING o trabajos FAILED que tengan pocos reintentos
        query = db.query(PrintJob).filter(
            (PrintJob.status == "PENDING") | 
            ((PrintJob.status == "FAILED") & (PrintJob.attempts < 3))
        )
        
        if target_device:
            query = query.filter(PrintJob.target_device == target_device)
        
        jobs = query.order_by(PrintJob.created_at.asc()).limit(5).all()
        
        # Marcar como IN_FLIGHT para el poller actual
        for job in jobs:
            job.status = "IN_FLIGHT"
            job.last_attempt = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            job.attempts += 1
        
        db.commit()
        return jobs
    except Exception as e:
        logger.error(f"Error en poller de impresión: {e}")
        return []

@router.patch("/{job_id}/status")
def update_job_status(job_id: str, update: PrintJobStatusUpdate, db: Session = Depends(get_db)):
    """
    Actualiza el estado de un trabajo tras el intento de impresión (ACK desde el Hardware/App).
    """
    job = db.query(PrintJob).get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo de impresión no encontrado")
    
    job.status = update.status
    if update.error_log:
        job.error_log = update.error_log
        logger.warning(f"[PRINT] Job {job_id} fallido: {update.error_log}")
    else:
        logger.info(f"[PRINT] Job {job_id} confirmado exitosamente.")
    
    db.commit()
    return {"status": "success", "job_id": job_id, "new_status": update.status}

@router.get("/", response_model=List[PrintJobOut])
def list_all_jobs(limit: int = 50, db: Session = Depends(get_db), current_user: Usuario = Depends(require_manager)):
    """
    Listado histórico de trabajos de impresión para auditoría.
    """
    return db.query(PrintJob).order_by(PrintJob.created_at.desc()).limit(limit).all()
