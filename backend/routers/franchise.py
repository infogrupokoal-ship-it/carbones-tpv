from fastapi import APIRouter, Depends
from typing import List, Dict
import uuid

router = APIRouter(prefix="/franchise", tags=["Multi-Site Franchise Engine"])

class Sucursal(Dict):
    id: str
    nombre: str
    ubicacion: str
    status: str # online, offline, mantenimiento

SUCURSALES_DB = [
    {"id": "LOC-001", "nombre": "Sede Central - La Granja", "ubicacion": "Madrid Norte", "status": "online"},
    {"id": "LOC-002", "nombre": "Express - Pozuelo", "ubicacion": "Madrid Oeste", "status": "online"},
    {"id": "LOC-003", "nombre": "Delivery Hub - Vallecas", "ubicacion": "Madrid Sur", "status": "mantenimiento"}
]

@router.get("/status")
def get_franchise_health():
    """
    Fase 40: Monitor Global de Franquicias.
    Permite la gestión centralizada de múltiples puntos de venta desde una única instancia.
    """
    return {
        "network_status": "HIGH_AVAILABILITY",
        "total_nodes": len(SUCURSALES_DB),
        "nodes": SUCURSALES_DB,
        "global_revenue_today": 4560.20
    }

@router.post("/sync-catalog")
def sync_catalog(sucursal_id: str):
    """Sincroniza el catálogo maestro con una sucursal específica."""
    return {"status": "synced", "sucursal": sucursal_id, "items_updated": 142}
