"""
AI Privacy Filter
=================
Filtro de confidencialidad para evitar enviar datos sensibles a modelos no autorizados 
(ej. OpenRouter free models).
"""

import re
import logging

logger = logging.getLogger("shared_ai.ai_privacy")

# Regex básicas para detectar si hay PII (Personal Identifiable Information)
EMAIL_REGEX = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
PHONE_REGEX = re.compile(r"(?:\+34|0034|34)?[ -]*(?:6|7|8|9)[0-9]{2}[ -]*[0-9]{3}[ -]*[0-9]{3}")

def contains_sensitive_data(prompt: str, is_sensitive_flag: bool = False) -> bool:
    """
    Determina si un prompt contiene datos sensibles basándose en flags o regex de PII.
    """
    if is_sensitive_flag:
        return True
        
    if EMAIL_REGEX.search(prompt):
        logger.debug("[Privacy] Se detectó un correo electrónico en el prompt.")
        return True
        
    if PHONE_REGEX.search(prompt):
        logger.debug("[Privacy] Se detectó un número de teléfono en el prompt.")
        return True
        
    # Añadir comprobaciones de tarjetas de crédito o DNIs si fuera necesario.
    return False
