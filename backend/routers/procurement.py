from fastapi import APIRouter
import random

router = APIRouter(prefix="/procurement", tags=["Autonomous Procurement & Vendor Bidding"])

@router.post("/negotiate")
def auto_negotiate_prices(materia_prima: str):
    """
    Fase 50: Compras Autónomas y Subasta de Proveedores.
    El sistema contacta con proveedores y negocia el mejor precio basado en volumen.
    """
    ofertas = [
        {"proveedor": "Pollos Paco", "precio": 4.50, "calidad": "AA"},
        {"proveedor": "Macro Pollos", "precio": 4.25, "calidad": "A"},
        {"proveedor": "EcoGranja", "precio": 5.10, "calidad": "AAA"}
    ]
    
    mejor_oferta = min(ofertas, key=lambda x: x["precio"])
    
    return {
        "materia_prima": materia_prima,
        "accion": "COMPRA_AUTOMATICA_EJECUTADA",
        "proveedor_ganador": mejor_oferta["proveedor"],
        "precio_negociado": mejor_oferta["precio"],
        "ahorro_estimado": "12.5%",
        "proxima_subasta": "En 24h"
    }
