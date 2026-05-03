from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class ESGMetrics(BaseModel):
    co2_ahorrado_kg: float
    comida_donada_kg: float
    envases_eco_usados: int
    energia_renovable_porcentaje: float
    incidentes_laborales: int
    horas_formacion_empleados: int

# Mock Database for ESG
current_esg_data = ESGMetrics(
    co2_ahorrado_kg=450.5,
    comida_donada_kg=120.0,
    envases_eco_usados=8500,
    energia_renovable_porcentaje=45.0,
    incidentes_laborales=0,
    horas_formacion_empleados=120
)

class ESGReport(BaseModel):
    mes: str
    metricas: ESGMetrics
    puntuacion_global: int

db_esg_reports = [
    ESGReport(mes="2026-04", metricas=ESGMetrics(
        co2_ahorrado_kg=400.0,
        comida_donada_kg=110.0,
        envases_eco_usados=8000,
        energia_renovable_porcentaje=40.0,
        incidentes_laborales=0,
        horas_formacion_empleados=100
    ), puntuacion_global=85)
]

@router.get("/esg/current", response_model=ESGMetrics)
async def get_current_esg_metrics():
    """Obtener métricas ESG en tiempo real (acumuladas del mes actual)"""
    return current_esg_data

@router.get("/esg/reports", response_model=List[ESGReport])
async def get_esg_reports():
    """Obtener el histórico de reportes ESG mensuales"""
    return db_esg_reports

@router.post("/esg/log-donation")
async def log_food_donation(kilos: float, organizacion: str):
    """Registrar una donación de excedentes de comida (Food Waste Reduction)"""
    current_esg_data.comida_donada_kg += kilos
    # Aquí se guardaría en BD real con la organización destinataria
    return {"status": "success", "message": f"{kilos}kg donados registrados exitosamente para {organizacion}."}

@router.post("/esg/log-eco-packaging")
async def log_eco_packaging_usage(cantidad: int):
    """Registrar el uso de envases biodegradables/reciclables"""
    current_esg_data.envases_eco_usados += cantidad
    return {"status": "success", "message": f"{cantidad} envases ecológicos registrados."}

@router.get("/esg/dashboard")
async def get_esg_dashboard_summary():
    """Resumen para el dashboard principal de ESG"""
    return {
        "impacto_ambiental": {
            "estado": "EXCELENTE",
            "co2_ahorrado": f"{current_esg_data.co2_ahorrado_kg} kg",
            "tendencia": "+12% vs mes anterior"
        },
        "impacto_social": {
            "estado": "BUENO",
            "comida_donada": f"{current_esg_data.comida_donada_kg} kg",
            "horas_formacion": current_esg_data.horas_formacion_empleados
        },
        "gobernanza": {
            "estado": "ÓPTIMO",
            "incidentes": current_esg_data.incidentes_laborales
        },
        "certificacion_sostenibilidad": "EN TRAMITE"
    }
