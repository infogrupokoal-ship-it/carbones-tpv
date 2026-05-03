from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
import datetime
import uuid

router = APIRouter(prefix="/mantenimiento", tags=["Mantenimiento Preventivo (IoT)"])

class EquipoBase(BaseModel):
    nombre: str
    tipo: str # FREIDORA, ASADOR, CAMARA_FRIGORIFICA, TPV
    ubicacion: str

class EquipoOut(EquipoBase):
    id: str
    estado: str # OPERATIVO, MANTENIMIENTO_REQUERIDO, AVERIADO
    proxima_revision: datetime.date
    vida_util_restante_dias: int

class RegistroMantenimiento(BaseModel):
    equipo_id: str
    accion_realizada: str
    coste: float

# Base de datos en memoria para prototipado
EQUIPOS_DB = [
    EquipoOut(id=str(uuid.uuid4()), nombre="Asador Rotativo #1", tipo="ASADOR", ubicacion="Cocina Caliente", estado="OPERATIVO", proxima_revision=datetime.date(2026, 6, 1), vida_util_restante_dias=800),
    EquipoOut(id=str(uuid.uuid4()), nombre="Freidora Alto Rendimiento", tipo="FREIDORA", ubicacion="Cocina Caliente", estado="MANTENIMIENTO_REQUERIDO", proxima_revision=datetime.date.today(), vida_util_restante_dias=300),
]

@router.get("/equipos", response_model=List[EquipoOut])
def listar_equipos():
    """Fase 22: Listado del parque de maquinaria y hardware del restaurante."""
    return EQUIPOS_DB

@router.post("/registrar-accion")
def registrar_accion(reg: RegistroMantenimiento):
    """
    Registra cambios de aceite, limpieza de filtros o mantenimiento de hardware.
    Genera un asiento de gasto automático.
    """
    return {
        "status": "success",
        "mensaje": f"Mantenimiento registrado para el equipo {reg.equipo_id}. Coste {reg.coste}€ imputado a la cuenta de explotación.",
        "proxima_revision_recomendada": (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
    }
