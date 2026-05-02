from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

router = APIRouter(prefix="/reservas", tags=["Reservas & Dine-in"])

class MesaBase(BaseModel):
    numero: int
    capacidad: int
    zona: str # TERRAZA, INTERIOR, VIP

class MesaOut(MesaBase):
    id: str
    ocupada: bool

class ReservaCreate(BaseModel):
    cliente_nombre: str
    telefono: str
    comensales: int = Field(..., gt=0, le=20)
    fecha_hora: datetime
    notas_especiales: str = ""

class ReservaOut(ReservaCreate):
    id: str
    estado: str # PENDIENTE, CONFIRMADA, CANCELADA, COMPLETADA
    mesa_asignada_id: str = None

# Base de datos en memoria para el prototipo industrializado
MESAS_DB = [
    MesaOut(id=str(uuid.uuid4()), numero=1, capacidad=4, zona="INTERIOR", ocupada=False),
    MesaOut(id=str(uuid.uuid4()), numero=2, capacidad=2, zona="INTERIOR", ocupada=False),
    MesaOut(id=str(uuid.uuid4()), numero=10, capacidad=6, zona="TERRAZA", ocupada=False),
    MesaOut(id=str(uuid.uuid4()), numero=20, capacidad=10, zona="VIP", ocupada=False),
]

RESERVAS_DB = []

@router.get("/mesas", response_model=List[MesaOut])
def listar_mesas():
    """Obtiene el mapa de mesas en tiempo real."""
    return MESAS_DB

@router.post("/", response_model=ReservaOut)
def crear_reserva(reserva: ReservaCreate):
    """Crea una reserva y busca asignarle mesa automáticamente (Omnicanal)."""
    nueva = ReservaOut(
        id=str(uuid.uuid4()),
        estado="PENDIENTE",
        **reserva.dict()
    )
    
    # Lógica ultra simple de asignación
    for mesa in MESAS_DB:
        if not mesa.ocupada and mesa.capacidad >= nueva.comensales:
            nueva.mesa_asignada_id = mesa.id
            nueva.estado = "CONFIRMADA"
            # Mesa queda reservada (en la vida real depende de hora, aquí simplificado)
            mesa.ocupada = True 
            break
            
    RESERVAS_DB.append(nueva)
    return nueva

@router.get("/", response_model=List[ReservaOut])
def listar_reservas():
    """Listado del panel de control para el Maître/Host."""
    return RESERVAS_DB
