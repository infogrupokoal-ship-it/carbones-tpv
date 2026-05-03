"""
AI Task Lock & Quota State
==========================
Controla el estado global de cuota para que todos los bots en un mismo servidor
sepan cuándo la IA está en Modo Degradado, sin pisarse.
"""

import json
import os
import time
import logging

logger = logging.getLogger("shared_ai.ai_task_lock")

QUOTA_STATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "agent_memory",
    "ai_quota_state.json"
)

# 15 minutos de cooldown por defecto
DEFAULT_COOLDOWN_SECONDS = 900 

def _ensure_dir_exists():
    os.makedirs(os.path.dirname(QUOTA_STATE_FILE), exist_ok=True)

def read_quota_state() -> dict:
    _ensure_dir_exists()
    if not os.path.exists(QUOTA_STATE_FILE):
        return {
            "is_degraded": False,
            "fallback_time": 0,
            "cooldown_seconds": DEFAULT_COOLDOWN_SECONDS
        }
    
    try:
        with open(QUOTA_STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"[TaskLock] Error leyendo quota state: {e}")
        return {
            "is_degraded": False,
            "fallback_time": 0,
            "cooldown_seconds": DEFAULT_COOLDOWN_SECONDS
        }

def write_quota_state(is_degraded: bool, cooldown_seconds: int = DEFAULT_COOLDOWN_SECONDS):
    _ensure_dir_exists()
    state = {
        "is_degraded": is_degraded,
        "fallback_time": time.time() if is_degraded else 0,
        "cooldown_seconds": cooldown_seconds
    }
    try:
        with open(QUOTA_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4)
    except Exception as e:
        logger.error(f"[TaskLock] Error escribiendo quota state: {e}")

def check_is_degraded() -> bool:
    """Verifica si el sistema está en modo degradado y si ya pasó el cooldown."""
    state = read_quota_state()
    if not state.get("is_degraded", False):
        return False
        
    fallback_time = state.get("fallback_time", 0)
    cooldown = state.get("cooldown_seconds", DEFAULT_COOLDOWN_SECONDS)
    
    if time.time() - fallback_time > cooldown:
        # El cooldown expiró, intentar recuperar
        logger.info("[TaskLock] Cooldown expirado. Saliendo del modo degradado.")
        write_quota_state(False)
        return False
        
    return True

def get_remaining_cooldown() -> int:
    state = read_quota_state()
    if not state.get("is_degraded", False):
        return 0
    
    fallback_time = state.get("fallback_time", 0)
    cooldown = state.get("cooldown_seconds", DEFAULT_COOLDOWN_SECONDS)
    elapsed = time.time() - fallback_time
    return max(0, int(cooldown - elapsed))
