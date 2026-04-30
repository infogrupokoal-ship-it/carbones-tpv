from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from .config import settings

# Contexto de hashing profesional
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """Genera un JWT seguro para la sesión del usuario."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña o PIN contra su hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera un hash seguro irreversible (Bcrypt)."""
    return pwd_context.hash(password)

def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
    """Alias para claridad en el contexto de TPV."""
    return verify_password(plain_pin, hashed_pin)

def get_pin_hash(pin: str) -> str:
    """Alias para claridad en el contexto de TPV."""
    return get_password_hash(pin)
