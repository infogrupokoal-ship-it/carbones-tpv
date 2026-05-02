from fastapi import APIRouter
import random

router = APIRouter(prefix="/iot", tags=["Industrial IoT & Predictive Maintenance"])

@router.get("/status/{maquina_id}")
def get_machine_telemetry(maquina_id: str):
    """
    Fase 42: Telemetría Industrial IoT.
    Simula la lectura de sensores (temperatura, vibración) y predice fallos.
    """
    temp = random.uniform(180, 220) # Grados Celsius (parrilla)
    vibracion = random.uniform(0.1, 0.5)
    
    # Lógica de predicción IA
    prob_fallo = (temp - 180) / 40 + vibracion
    necesita_tecnico = prob_fallo > 0.8
    
    return {
        "maquina_id": maquina_id,
        "telemetria": {
            "temperatura": f"{round(temp, 1)}°C",
            "vibracion": f"{round(vibracion, 2)}mm/s"
        },
        "probabilidad_fallo_7d": f"{round(prob_fallo * 100, 1)}%",
        "recomendacion": "MANTENIMIENTO_URGENTE" if necesita_tecnico else "OPERATIVO_NORMAL"
    }
