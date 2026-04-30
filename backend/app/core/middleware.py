import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from ..models.audit import AuditLog
from .database import SessionLocal

class EnterpriseAuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Solo auditamos métodos que modifican datos
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            # Clonamos el cuerpo para no consumirlo antes de que llegue al endpoint
            body_bytes = await request.body()
            
            # Continuamos con la petición
            response = await call_next(request)
            
            # Si la petición fue exitosa, registramos el log
            if response.status_code < 400:
                db = SessionLocal()
                try:
                    # Intentamos obtener el usuario del token si existe
                    # (Esto se puede mejorar extrayendo el user_id del payload JWT si ya se ha validado)
                    user_id = request.headers.get("X-User-ID", "SYSTEM")
                    
                    log = AuditLog(
                        usuario_id=user_id,
                        accion=f"{request.method} {request.url.path}",
                        tabla_afectada="API_V1",
                        registro_id="N/A",
                        valor_nuevo=body_bytes.decode("utf-8") if body_bytes else None,
                        ip_address=request.client.host if request.client else "Unknown"
                    )
                    db.add(log)
                    db.commit()
                except Exception as e:
                    print(f"Error registrando auditoría: {e}")
                finally:
                    db.close()
            return response
        
        return await call_next(request)
