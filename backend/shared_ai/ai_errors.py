"""
Universal AI Error Classifier
=============================
Estandariza los errores de Google Generative AI (Gemini), OpenRouter, etc.,
en categorías de error universales para que el router sepa cómo proceder.
"""

from enum import Enum
import logging

logger = logging.getLogger("shared_ai.ai_errors")

class AIErrorCategory(Enum):
    OK = "OK"
    CLAVE_INVALIDA = "CLAVE_INVALIDA"
    BILLING = "BILLING"
    CUOTA = "CUOTA"
    MODELO_NO_SOPORTADO = "MODELO_NO_SOPORTADO"
    VARIABLE = "VARIABLE"
    RED = "RED"
    LIBRERIA = "LIBRERIA"
    DESCONOCIDO = "DESCONOCIDO"

QUOTA_KEYWORDS = [
    "quota",
    "429",
    "resource_exhausted",
    "rate_limit",
    "too many requests"
]

BILLING_KEYWORDS = [
    "billing",
    "payment",
    "credit"
]

MODEL_KEYWORDS = [
    "not found",
    "404",
    "not supported",
    "model"
]

def classify_ai_error(error: Exception) -> AIErrorCategory:
    """Clasifica una excepción cruda de la API en una AIErrorCategory."""
    err_str = str(error).lower()
    
    if any(kw in err_str for kw in QUOTA_KEYWORDS):
        return AIErrorCategory.CUOTA
        
    if any(kw in err_str for kw in BILLING_KEYWORDS):
        return AIErrorCategory.BILLING
        
    if "api_key" in err_str or "unauthorized" in err_str or "401" in err_str or "403" in err_str:
        return AIErrorCategory.CLAVE_INVALIDA
        
    if any(kw in err_str for kw in MODEL_KEYWORDS):
        return AIErrorCategory.MODELO_NO_SOPORTADO
        
    if "timeout" in err_str or "connection" in err_str or "network" in err_str:
        return AIErrorCategory.RED
        
    return AIErrorCategory.DESCONOCIDO
