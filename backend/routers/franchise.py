from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

class FranchiseeBase(BaseModel):
    nombre: str
    ubicacion: str
    contacto: str
    fecha_apertura: Optional[str] = None
    estado: str = "PROSPECTO" # PROSPECTO, ACTIVA, SUSPENDIDA

class Franchisee(FranchiseeBase):
    id: int
    royalties_pendientes: float = 0.0
    score_auditoria: int = 100

class RoyaltyPayment(BaseModel):
    franquicia_id: int
    monto: float
    fecha: str
    concepto: str

# Mock Database for Franchise
db_franchises = [
    Franchisee(id=1, nombre="Carbones Madrid Centro", ubicacion="Calle Gran Vía 12", contacto="madrid@carbones.com", fecha_apertura="2024-01-15", estado="ACTIVA", royalties_pendientes=1200.50, score_auditoria=95),
    Franchisee(id=2, nombre="Carbones Valencia Playa", ubicacion="Paseo Marítimo 4", contacto="valencia@carbones.com", fecha_apertura="2025-03-10", estado="ACTIVA", royalties_pendientes=0.0, score_auditoria=98),
    Franchisee(id=3, nombre="Carbones Sevilla", ubicacion="Plaza España 1", contacto="sevilla@carbones.com", estado="PROSPECTO", royalties_pendientes=0.0, score_auditoria=0)
]

@router.get("/franchises", response_model=List[Franchisee])
async def get_franchises():
    """Obtener todas las franquicias registradas"""
    return db_franchises

@router.post("/franchises", response_model=Franchisee)
async def create_franchise(franchise: FranchiseeBase):
    """Dar de alta una nueva franquicia (prospecto o activa)"""
    new_id = len(db_franchises) + 1
    new_franchise = Franchisee(id=new_id, **franchise.dict())
    db_franchises.append(new_franchise)
    return new_franchise

@router.get("/franchises/{franquicia_id}/metrics")
async def get_franchise_metrics(franquicia_id: int):
    """Métricas de rendimiento de una franquicia específica"""
    franq = next((f for f in db_franchises if f.id == franquicia_id), None)
    if not franq:
        raise HTTPException(status_code=404, detail="Franquicia no encontrada")
    
    # Mock metrics
    return {
        "ventas_mes_actual": 45000.00,
        "crecimiento_interanual": "+12%",
        "satisfaccion_cliente": 4.8,
        "score_auditoria": franq.score_auditoria,
        "royalties_pendientes": franq.royalties_pendientes
    }

@router.post("/franchises/audit")
async def register_audit(franquicia_id: int, score: int):
    """Registrar resultado de auditoría de calidad de una franquicia"""
    franq = next((f for f in db_franchises if f.id == franquicia_id), None)
    if not franq:
        raise HTTPException(status_code=404, detail="Franquicia no encontrada")
    
    franq.score_auditoria = score
    return {"status": "success", "message": f"Auditoría registrada. Nuevo score: {score}"}

@router.get("/franchises/overview")
async def get_network_overview():
    """Resumen global de la red de franquicias"""
    activas = sum(1 for f in db_franchises if f.estado == "ACTIVA")
    prospectos = sum(1 for f in db_franchises if f.estado == "PROSPECTO")
    total_royalties = sum(f.royalties_pendientes for f in db_franchises)
    
    return {
        "franquicias_activas": activas,
        "prospectos_en_cola": prospectos,
        "royalties_totales_pendientes": total_royalties,
        "score_promedio_red": sum(f.score_auditoria for f in db_franchises if f.estado == "ACTIVA") / max(1, activas)
    }
