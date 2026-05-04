
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, ConfigDict
from .dependencies import get_current_user

from ..database import get_db
from ..models import Usuario
from ..utils.auth import verify_password, create_access_token
from ..utils.logger import logger
# from .admin_audit import log_audit_action  <-- Movido a funciones para evitar circular import


router = APIRouter(prefix="/auth", tags=["Seguridad e Identidad"])

# --- Esquemas de Datos ---

class LoginRequest(BaseModel):
    username: str = Field(..., json_schema_extra={"example": "admin"})
    pin: str = Field(..., min_length=4, max_length=6, json_schema_extra={"example": "1234"})

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    rol: str  # alias para compatibilidad con frontend legacy
    username: str

class UserProfile(BaseModel):
    id: str
    username: str
    role: str = Field(..., alias="rol")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# --- Rutas de Autenticación ---

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Punto de entrada seguro: Valida las credenciales del operador (PIN) 
    y emite un token de acceso industrial cifrado.
    """
    try:
        import os
        if data.username == "admin" and data.pin == "1234" and os.environ.get("ENVIRONMENT", "local").lower() == "production":
            logger.warning("Intento de acceso bloqueado: PIN '1234' para admin no permitido en PRODUCCIÓN.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Por seguridad, el PIN '1234' está desactivado en producción. Por favor, cambie sus credenciales de acceso usando scripts/update_admin.py",
            )

        user = db.query(Usuario).filter(Usuario.username == data.username).first()
        
        # En el contexto TPV, el PIN es la credencial principal del empleado
        if not user or not verify_password(data.pin, user.pin_hash):
            logger.warning(f"Fallo de autenticación: Usuario '{data.username}'")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o código PIN incorrectos.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Generar token con claims de rol para control de acceso en frontend
        access_token = create_access_token(
            data={"sub": user.username, "role": user.rol}
        )
        
        logger.info(f"Sesión Iniciada: {user.username} (Rol: {user.rol})")
        
        # Auditoría de Seguridad
        from .admin_audit import log_audit_action
        log_audit_action(

            db=db,
            usuario_id=user.id,
            accion="LOGIN",
            entidad="USUARIO",
            entidad_id=user.id,
            payload_nuevo=f"Sesión iniciada con rol {user.rol}"
        )
        
        return TokenResponse(
            access_token=access_token,
            role=user.rol,
            rol=user.rol,
            username=user.username
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CRITICAL ERROR [Auth Login]: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno en el núcleo de autenticación: {str(e)}"
        )

@router.get("/me", response_model=UserProfile)
async def read_users_me(current_user: Usuario = Depends(get_current_user)):
    """
    Retorna el perfil del operador actual autenticado.
    """
    return current_user

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Finaliza la sesión del operador y registra el evento para auditoría.
    """
    logger.info(f"Sesión Cerrada: {current_user.username}")
    
    # Auditoría de Seguridad
    from .admin_audit import log_audit_action
    log_audit_action(

        db=db,
        usuario_id=current_user.id,
        accion="LOGOUT",
        entidad="USUARIO",
        entidad_id=current_user.id
    )
    
    return None
