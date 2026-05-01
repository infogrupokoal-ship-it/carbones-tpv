import uuid
import random
import string
import requests
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import jwt

from ..database import get_db
from ..models import Cliente, VerificacionOTP
from ..utils.logger import logger

router = APIRouter(prefix="/customers", tags=["Clientes y B2C"])

SECRET_KEY = "carbones_secreto_super_seguro_b2c"  # In a real app, use env var
ALGORITHM = "HS256"

WAHA_URL = "http://113.30.148.104:3000/api/sendText"
WAHA_API_KEY = "1060705b0a574d1fbc92fa10a2b5aca7"

class OTPRequest(BaseModel):
    telefono: str
    nombre: str = "Cliente"

class OTPVerify(BaseModel):
    telefono: str
    codigo: str

def enviar_whatsapp_waha(telefono: str, mensaje: str):
    # Formatear el teléfono a formato internacional si es español y no empieza por 34
    if len(telefono) == 9 and telefono.startswith(('6', '7')):
        telefono_wa = f"34{telefono}"
    else:
        telefono_wa = telefono

    payload = {"chatId": f"{telefono_wa}@c.us", "text": mensaje, "session": "default"}
    headers = {"Content-Type": "application/json", "X-Api-Key": WAHA_API_KEY}
    
    try:
        response = requests.post(WAHA_URL, json=payload, headers=headers, timeout=5)
        logger.info(f"OTP enviado a {telefono_wa} vía WAHA. Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Error al enviar OTP vía WhatsApp a {telefono_wa}: {e}")

@router.post("/request-otp")
def solicitar_otp(req: OTPRequest, db: Session = Depends(get_db)):
    codigo = ''.join(random.choices(string.digits, k=6))
    
    # Invalidate previous ones
    db.query(VerificacionOTP).filter(VerificacionOTP.telefono == req.telefono, VerificacionOTP.usado == False).update({"usado": True})
    
    nuevo_otp = VerificacionOTP(
        id=str(uuid.uuid4()),
        telefono=req.telefono,
        codigo=codigo,
        fecha_expiracion=datetime.utcnow() + timedelta(minutes=5)
    )
    db.add(nuevo_otp)
    
    # Send via WhatsApp
    mensaje = f"🍗🔥 Tu código de acceso rápido a Carbones y Pollos es: *{codigo}*. \n\n¡Gracias por tu pedido!"
    enviar_whatsapp_waha(req.telefono, mensaje)
    
    # Save the name if we want to remember it on signup
    cliente = db.query(Cliente).filter(Cliente.telefono == req.telefono).first()
    if not cliente:
        nuevo_cliente = Cliente(id=str(uuid.uuid4()), telefono=req.telefono, nombre=req.nombre)
        db.add(nuevo_cliente)

    db.commit()
    return {"status": "success", "message": "Código OTP enviado por WhatsApp"}

@router.post("/verify-otp")
def verificar_otp(req: OTPVerify, db: Session = Depends(get_db)):
    verificacion = db.query(VerificacionOTP).filter(
        VerificacionOTP.telefono == req.telefono,
        VerificacionOTP.codigo == req.codigo,
        VerificacionOTP.usado == False
    ).first()
    
    if not verificacion or verificacion.fecha_expiracion < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Código inválido o caducado")
        
    verificacion.usado = True
    
    cliente = db.query(Cliente).filter(Cliente.telefono == req.telefono).first()
    if not cliente:
        cliente = Cliente(id=str(uuid.uuid4()), telefono=req.telefono, nombre="Cliente")
        db.add(cliente)
        
    db.commit()
    
    # Generar Token JWT para que el frontend lo guarde
    token_data = {
        "sub": cliente.id, 
        "telefono": cliente.telefono, 
        "nombre": cliente.nombre, 
        "puntos": cliente.puntos_fidelidad,
        "nivel": cliente.nivel_fidelidad
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"status": "success", "token": token, "cliente": token_data}

@router.get("/me/orders")
def obtener_mis_pedidos(cliente_id: str, db: Session = Depends(get_db)):
    """
    Obtiene el historial de pedidos de un cliente. 
    Para un entorno B2C real se usaría JWT auth en el middleware, pero
    como es una PWA de Kiosko con baja fricción pasamos el ID directamente o validamos aquí.
    """
    from ..models import Pedido
    pedidos = db.query(Pedido).filter(Pedido.cliente_id == cliente_id).order_by(Pedido.fecha.desc()).limit(10).all()
    
    results = []
    for p in pedidos:
        results.append({
            "id": p.id,
            "numero_ticket": p.numero_ticket,
            "fecha": p.fecha.isoformat(),
            "estado": p.estado,
            "total": p.total,
            "origen": p.origen
        })
    return {"status": "success", "orders": results}
