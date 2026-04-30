from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.core import security
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.models.user import Usuario

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class LoginPIN(BaseModel):
    username: str
    pin: str

@router.post("/login/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login, para aplicaciones externas."""
    user = db.query(Usuario).filter(Usuario.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "role": user.rol
    }

@router.post("/login/pin", response_model=Token)
def login_pin(
    data: LoginPIN, db: Session = Depends(get_db)
) -> Any:
    """Login rápido mediante PIN para terminales TPV."""
    user = db.query(Usuario).filter(Usuario.username == data.username).first()
    if not user or not security.verify_pin(data.pin, user.pin_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o PIN incorrecto",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "role": user.rol
    }
