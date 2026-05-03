
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Usuario
from ..utils.auth import decode_access_token
from ..utils.logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

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

async def get_current_active_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """Verifica que el usuario no esté desactivado."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo.")
    return current_user

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
