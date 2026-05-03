"""
AI Budget & Limit Control
=========================
Controla límites lógicos por tarea (previene que un bot haga 50 peticiones en 1 min).
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Máximo número de veces que se puede llamar a Gemini dentro de un contexto de tarea/mensaje
AI_MAX_CALLS_PER_TASK = int(os.getenv("AI_MAX_CALLS_PER_TASK", "5"))

def check_task_budget(calls_made: int) -> bool:
    """Verifica si la tarea actual ha superado el límite de llamadas."""
    return calls_made < AI_MAX_CALLS_PER_TASK
