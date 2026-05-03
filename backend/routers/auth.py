
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, ConfigDict

from ..database import get_db
from ..models import Usuario
from ..utils.auth import verify_password, create_access_token, decode_access_token
from ..utils.logger import logger
# from .admin_audit import log_audit_action  <-- Movido a funciones para evitar circular import


router = APIRouter(prefix="/auth", tags=["Seguridad e Identidad"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# --- Esquemas de Datos ---

class LoginRequest(BaseModel):
    username: str = Field(..., json_schema_extra={"example": "admin"})
    pin: str = Field(..., min_length=4, max_length=6, json_schema_extra={"example": "1234"})

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str

class UserProfile(BaseModel):
    id: str
    username: str
    role: str = Field(..., alias="rol")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# --- Dependencias de Seguridad ---

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    """
    Validación de identidad centralizada mediante JWT. 
    Verifica la integridad del token y la existencia del usuario en el sistema.
    """
    payload = decode_access_token(token)
    if not payload:
        logger.warning("Intento de acceso con token inválido o expirado.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La sesión ha expirado o es inválida. Por favor, identifíquese de nuevo.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    user = db.query(Usuario).filter(Usuario.username == username).first()
    
    if not user:
        logger.error(f"Token válido para usuario inexistente: {username}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Identidad de usuario no encontrada."
        )
    
    return user

class RoleChecker:
    """Validador de roles para endpoints protegidos."""
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: Usuario = Depends(get_current_user)) -> Usuario:
        if current_user.rol not in self.allowed_roles:
            logger.warning(f"Acceso denegado (RBAC): Usuario '{current_user.username}' (Rol: {current_user.rol}) intentó acceder a un recurso restringido.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operación denegada: Privilegios insuficientes."
            )
        return current_user

# Pre-configuraciones de roles
require_admin = RoleChecker(["ADMIN"])
require_manager = RoleChecker(["ADMIN", "MANAGER"])

# --- Rutas de Autenticación ---

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Punto de entrada seguro: Valida las credenciales del operador (PIN) 
    y emite un token de acceso industrial cifrado.
    """
    try:
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
