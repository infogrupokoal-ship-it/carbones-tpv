from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from ..utils.logger import logger
import traceback

class TPVException(Exception):
    """Excepción base para errores específicos del negocio TPV."""
    def __init__(self, message: str, status_code: int = 400, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

async def global_exception_handler(request: Request, exc: Exception):
    """Captura cualquier error no manejado y lo devuelve de forma profesional."""
    
    status_code = 500
    message = "Error interno del servidor"
    details = {}

    if isinstance(exc, TPVException):
        status_code = exc.status_code
        message = exc.message
        details = exc.details
    elif isinstance(exc, HTTPException):
        status_code = exc.status_code
        message = exc.detail
    else:
        # Error inesperado: Loguear stack trace completo para debugging
        logger.error(f"ERROR CRÍTICO: {request.method} {request.url.path}")
        logger.error(traceback.format_exc())

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "message": message,
            "details": details,
            "path": request.url.path
        }
    )
