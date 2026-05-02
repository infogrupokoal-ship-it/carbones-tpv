from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict
from backend.database import get_db
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/escandallos", tags=["Escandallos & Costes de Receta"])

class IngredienteCosto(BaseModel):
    nombre: str
    cantidad: float # ej: 0.5 (kg)
    unidad: str # kg, litro, unidad
    costo_unitario: float

class RecetaOut(BaseModel):
    plato_id: str
    nombre_plato: str
    costo_total_materia_prima: float
    precio_venta_sugerido: float
    margen_bruto_porcentaje: float

# Datos simulados para el motor de escandallos industrial
RECETAS_DB = [
    {
        "id": "R1",
        "nombre": "Pollo Asado Tradicional",
        "ingredientes": [
            {"nombre": "Pollo Entero", "cantidad": 1, "unidad": "un", "costo": 3.50},
            {"nombre": "Aceite Especias", "cantidad": 0.05, "unidad": "litro", "costo": 0.50},
            {"nombre": "Leña Encina", "cantidad": 0.2, "unidad": "kg", "costo": 0.20},
        ],
        "pvp": 12.50
    }
]

@router.get("/analisis", response_model=List[RecetaOut])
def analizar_margenes():
    """
    Fase 31: Módulo de Escandallos.
    Calcula el coste real de cada plato y el margen de beneficio.
    """
    resultados = []
    for r in RECETAS_DB:
        costo_total = sum(i["costo"] for i in r["ingredientes"])
        margen = ((r["pvp"] - costo_total) / r["pvp"]) * 100
        resultados.append(RecetaOut(
            plato_id=r["id"],
            nombre_plato=r["nombre"],
            costo_total_materia_prima=costo_total,
            precio_venta_sugerido=r["pvp"],
            margen_bruto_porcentaje=round(margen, 2)
        ))
    return resultados

@router.post("/simular-coste")
def simular_coste(ingredientes: List[IngredienteCosto], pvp_objetivo: float):
    """Permite simular el coste de un nuevo plato antes de añadirlo al menú."""
    costo_total = sum(i.cantidad * i.costo_unitario for i in ingredientes)
    margen = ((pvp_objetivo - costo_total) / pvp_objetivo) * 100 if pvp_objetivo > 0 else 0
    return {
        "costo_total_estimado": round(costo_total, 2),
        "margen_proyectado": f"{round(margen, 2)}%",
        "viabilidad": "ALTA" if margen > 60 else "BAJA (Revisar costes)"
    }
