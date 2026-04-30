from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ....core.database import get_db
from ....core.security import verify_pin, create_access_token
from ....models.user import Usuario

router = APIRouter()

@router.post("/login")
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    # En nuestro TPV usamos el PIN como password en el campo username o password
    user = db.query(Usuario).filter(Usuario.username == form_data.username).first()
    if not user or not verify_pin(form_data.password, user.pin_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="PIN o Usuario incorrecto",
        )
    
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer", "user": {"name": user.full_name, "role": user.rol}}
