from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Usuario
from ..utils.auth import verify_password, create_access_token, decode_access_token
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Autenticación"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

class LoginRequest(BaseModel):
    username: str
    pin: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
    username: str = payload.get("sub")
    user = db.query(Usuario).filter(Usuario.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.post("/login", response_model=Token)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.username == data.username).first()
    
    # En la TPV usamos PIN, pero lo tratamos con la seguridad de una contraseña
    if not user or not verify_password(data.pin, user.pin_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o PIN incorrecto",
        )
    
    access_token = create_access_token(data={"sub": user.username, "role": user.rol})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.rol
    }

@router.get("/me")
async def read_users_me(current_user: Usuario = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "rol": current_user.rol
    }
