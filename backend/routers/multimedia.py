from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..multimedia import manager
from ..utils.logger import logger
from .dependencies import get_current_active_user
from ..models import Usuario

router = APIRouter(prefix="/multimedia", tags=["Multimedia Industrial"])

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    category: str = Query("general", description="Categoría del archivo (facturas, fotos, audios, etc)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Subida industrial de archivos con validación de seguridad, hashing y persistencia.
    """
    try:
        content = await file.read()
        result = manager.process_file(
            db=db,
            file_content=content,
            original_filename=file.filename,
            user_id=current_user.id,
            category=category
        )
        
        logger.info(f"📁 ARCHIVO PROCESADO: {file.filename} por {current_user.username} [Category: {category}]")
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"❌ Error en subida multimedia: {e}")
        raise HTTPException(status_code=500, detail="Fallo interno en el pipeline multimedia")

@router.get("/list")
async def list_multimedia(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Lista archivos multimedia registrados en el sistema.
    """
    from ..models import Multimedia
    query = db.query(Multimedia)
    if category:
        query = query.filter(Multimedia.category == category)
    
    files = query.order_by(Multimedia.created_at.desc()).all()
    return files

@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Recupera un archivo físico mediante su ID de registro.
    """
    from ..models import Multimedia
    from fastapi.responses import FileResponse
    
    record = db.query(Multimedia).filter(Multimedia.id == file_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
    if not os.path.exists(record.file_path):
        raise HTTPException(status_code=404, detail="El archivo físico ha sido movido o eliminado")
        
    return FileResponse(
        path=record.file_path,
        filename=record.original_name,
        media_type=record.mime_type
    )

import os
