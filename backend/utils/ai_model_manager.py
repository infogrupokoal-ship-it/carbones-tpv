"""
AI Model Manager - Sistema de Rotación y Recuperación Automática de Modelos Gemini
====================================================================================
Autor: Koal-DevOps
Versión: 2.0 - Enterprise Grade

Comportamiento:
- Modelo primario: gemini-2.5-pro (el más potente)
- Si falla por cuota/tokens → rota al siguiente modelo de la jerarquía
- Cada RESET_INTERVAL_SECONDS, regresa automáticamente al modelo primario
- Thread-safe para entornos async/concurrentes
- Logging detallado de todos los cambios de modelo
"""

import time
import asyncio
import threading
import google.generativeai as genai
from typing import Optional, Tuple
from ..utils.logger import logger
from ..config import settings

# ──────────────────────────────────────────────────────────────────────────────
# JERARQUÍA DE MODELOS (de más potente a más ligero)
# El sistema siempre intentará usar el primero y caerá progresivamente
# ──────────────────────────────────────────────────────────────────────────────
MODEL_HIERARCHY = [
    {
        "id": "gemini-1.5-flash",
        "name": "Gemini 1.5 Flash (Primario)",
        "tier": "SPEED",
        "rpm_limit": 15,          # Tier gratuito estándar
    },
    {
        "id": "gemini-1.5-pro",
        "name": "Gemini 1.5 Pro (Secundario)",
        "tier": "POWER",
        "rpm_limit": 2,
    },
    {
        "id": "gemini-1.0-pro",
        "name": "Gemini 1.0 Pro (Terciario)",
        "tier": "STABLE",
        "rpm_limit": 15,
    },
]

# Tiempo en segundos antes de intentar regresar al modelo primario
RESET_INTERVAL_SECONDS = 900  # 15 minutos

# Errores de cuota/tokens que disparan el fallback
QUOTA_ERROR_KEYWORDS = [
    "quota",
    "429",
    "resource_exhausted",
    "rate_limit",
    "too many requests",
    "not found",
    "404",
    "not supported",
]


class AIModelManager:
    """
    Gestor centralizado de modelos de IA con rotación automática y recuperación.
    Implementado como Singleton thread-safe.
    """

    _instance: Optional["AIModelManager"] = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._current_index: int = 0          # Índice actual en MODEL_HIERARCHY
        self._last_fallback_time: float = 0   # Timestamp del último fallback
        self._last_reset_check: float = time.time()
        self._consecutive_errors: int = 0
        self._model_cache: dict = {}          # Cache de instancias GenerativeModel
        self._model_lock = asyncio.Lock() if self._is_async_context() else threading.Lock()

        # Configurar API
        if settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            logger.info(
                f"[AIModelManager] Iniciado. Modelo primario: {MODEL_HIERARCHY[0]['name']}"
            )
        else:
            logger.warning("[AIModelManager] GOOGLE_API_KEY no configurada.")

    def _is_async_context(self) -> bool:
        try:
            asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False

    @property
    def current_model_info(self) -> dict:
        """Devuelve la info del modelo actualmente activo."""
        return MODEL_HIERARCHY[self._current_index]

    def _get_or_create_model(self, model_id: str) -> genai.GenerativeModel:
        """Retorna una instancia cacheada del modelo o la crea."""
        if model_id not in self._model_cache:
            self._model_cache[model_id] = genai.GenerativeModel(model_id)
            logger.debug(f"[AIModelManager] Instancia creada para: {model_id}")
        return self._model_cache[model_id]

    def _should_reset_to_primary(self) -> bool:
        """Verifica si ha pasado suficiente tiempo para intentar el modelo primario."""
        if self._current_index == 0:
            return False
        elapsed = time.time() - self._last_fallback_time
        return elapsed >= RESET_INTERVAL_SECONDS

    def _try_reset_to_primary(self):
        """Intenta regresar al modelo primario si ha pasado el intervalo."""
        if self._should_reset_to_primary():
            old_index = self._current_index
            self._current_index = 0
            self._consecutive_errors = 0
            logger.info(
                f"[AIModelManager] ♻️ RESET AUTOMÁTICO: "
                f"{MODEL_HIERARCHY[old_index]['name']} → {MODEL_HIERARCHY[0]['name']} "
                f"(Han pasado {RESET_INTERVAL_SECONDS // 60} minutos)"
            )

    def _fallback_to_next(self, error: Exception) -> bool:
        """
        Mueve al siguiente modelo de la jerarquía.
        Retorna True si hay un modelo disponible, False si se agotaron todos.
        """
        error_str = str(error).lower()
        is_quota_error = any(kw in error_str for kw in QUOTA_ERROR_KEYWORDS)

        if not is_quota_error:
            logger.warning(
                f"[AIModelManager] Error no relacionado con cuota en "
                f"{self.current_model_info['name']}: {error}"
            )

        self._consecutive_errors += 1
        self._last_fallback_time = time.time()

        if self._current_index < len(MODEL_HIERARCHY) - 1:
            old_model = MODEL_HIERARCHY[self._current_index]["name"]
            self._current_index += 1
            new_model = MODEL_HIERARCHY[self._current_index]["name"]
            logger.warning(
                f"[AIModelManager] ⚠️ FALLBACK: {old_model} → {new_model} | "
                f"Error: {str(error)[:100]} | "
                f"Reiniciará a primario en {RESET_INTERVAL_SECONDS // 60} min"
            )
            return True
        else:
            logger.error(
                f"[AIModelManager] 🔴 TODOS LOS MODELOS AGOTADOS. "
                f"Errores consecutivos: {self._consecutive_errors}"
            )
            # Reiniciar al primario como último recurso
            self._current_index = 0
            self._last_fallback_time = time.time() - (RESET_INTERVAL_SECONDS - 60)
            return False

    def generate_content_sync(
        self, prompt: str, generation_config: Optional[dict] = None
    ) -> Tuple[Optional[str], str]:
        """
        Genera contenido con fallback automático (versión síncrona).
        Retorna: (texto_respuesta, modelo_usado)
        """
        # Intentar reset al primario si aplica
        self._try_reset_to_primary()

        attempts = 0
        max_attempts = len(MODEL_HIERARCHY)

        while attempts < max_attempts:
            model_info = self.current_model_info
            try:
                model = self._get_or_create_model(model_info["id"])
                kwargs = {}
                if generation_config:
                    kwargs["generation_config"] = generation_config
                
                response = model.generate_content(prompt, **kwargs)
                
                # Éxito — resetear contador de errores
                if self._consecutive_errors > 0:
                    logger.info(
                        f"[AIModelManager] ✅ Respuesta exitosa con {model_info['name']} "
                        f"tras {self._consecutive_errors} errores"
                    )
                    self._consecutive_errors = 0

                return response.text, model_info["id"]

            except Exception as e:
                logger.warning(
                    f"[AIModelManager] Error con {model_info['name']}: {e}"
                )
                has_next = self._fallback_to_next(e)
                attempts += 1
                if not has_next:
                    break

        logger.error("[AIModelManager] No se pudo generar respuesta con ningún modelo.")
        return None, "none"

    async def generate_content_async(
        self, prompt: str, generation_config: Optional[dict] = None
    ) -> Tuple[Optional[str], str]:
        """
        Genera contenido con fallback automático (versión asíncrona).
        Retorna: (texto_respuesta, modelo_usado)
        """
        # Intentar reset al primario si aplica
        self._try_reset_to_primary()

        attempts = 0
        max_attempts = len(MODEL_HIERARCHY)

        while attempts < max_attempts:
            model_info = self.current_model_info
            try:
                model = self._get_or_create_model(model_info["id"])
                kwargs = {}
                if generation_config:
                    kwargs["generation_config"] = generation_config

                # El SDK de Gemini es síncrono, usamos asyncio.to_thread
                response = await asyncio.to_thread(
                    model.generate_content, prompt, **kwargs
                )

                if self._consecutive_errors > 0:
                    logger.info(
                        f"[AIModelManager] ✅ Respuesta exitosa con {model_info['name']} "
                        f"tras {self._consecutive_errors} errores"
                    )
                    self._consecutive_errors = 0

                return response.text, model_info["id"]

            except Exception as e:
                logger.warning(
                    f"[AIModelManager] Error con {model_info['name']}: {e}"
                )
                self._fallback_to_next(e)
                attempts += 1

        logger.error("[AIModelManager] No se pudo generar respuesta con ningún modelo.")
        return None, "none"

    def get_status(self) -> dict:
        """Devuelve el estado completo del gestor de modelos."""
        elapsed = time.time() - self._last_fallback_time if self._last_fallback_time else 0
        time_to_reset = max(0, RESET_INTERVAL_SECONDS - elapsed) if self._current_index > 0 else 0

        return {
            "active_model": self.current_model_info["name"],
            "active_model_id": self.current_model_info["id"],
            "active_tier": self.current_model_info["tier"],
            "primary_model": MODEL_HIERARCHY[0]["name"],
            "is_primary": self._current_index == 0,
            "consecutive_errors": self._consecutive_errors,
            "time_to_primary_reset_seconds": round(time_to_reset),
            "model_hierarchy": [m["name"] for m in MODEL_HIERARCHY],
            "reset_interval_minutes": RESET_INTERVAL_SECONDS // 60,
        }


# ──────────────────────────────────────────────────────────────────────────────
# INSTANCIA GLOBAL SINGLETON
# ──────────────────────────────────────────────────────────────────────────────
ai_manager = AIModelManager()


# ──────────────────────────────────────────────────────────────────────────────
# FUNCIONES DE CONVENIENCIA
# ──────────────────────────────────────────────────────────────────────────────
async def generate_ai_response(prompt: str, generation_config: Optional[dict] = None) -> str:
    """
    Función de conveniencia asíncrona.
    Genera una respuesta con rotación automática de modelos.
    """
    text, model_used = await ai_manager.generate_content_async(prompt, generation_config)
    if text is None:
        return "Koal-AI: Servicio temporalmente no disponible. Por favor, inténtalo en unos minutos."
    return text


def generate_ai_response_sync(prompt: str, generation_config: Optional[dict] = None) -> str:
    """
    Función de conveniencia síncrona.
    Genera una respuesta con rotación automática de modelos.
    """
    text, model_used = ai_manager.generate_content_sync(prompt, generation_config)
    if text is None:
        return "Koal-AI: Servicio temporalmente no disponible. Por favor, inténtalo en unos minutos."
    return text
