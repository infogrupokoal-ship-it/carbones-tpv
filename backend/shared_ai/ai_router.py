"""
Enterprise AI Router
====================
Router centralizado unificado para todo el ecosistema Koal/Carbones.
Combina Gemini (varios modelos) y OpenRouter como último recurso.
"""

import os
import asyncio
import google.generativeai as genai
from typing import Optional, Tuple
import logging

from .ai_errors import classify_ai_error, AIErrorCategory
from .ai_task_lock import check_is_degraded, write_quota_state, get_remaining_cooldown
from .ai_privacy import contains_sensitive_data

logger = logging.getLogger("shared_ai.ai_router")

# Jerarquía
GEMINI_MODELS = [
    {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro"},
    {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash"},
    {"id": "gemini-1.5-pro-latest", "name": "Gemini 1.5 Pro"}
]

# Configuración
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class AIRouter:
    def __init__(self):
        self._model_cache = {}

    def _get_model(self, model_id: str, tools: list = None, system_instruction: str = None) -> genai.GenerativeModel:
        cache_key = f"{model_id}_{bool(tools)}_{bool(system_instruction)}"
        if cache_key not in self._model_cache:
            kwargs = {}
            if tools:
                kwargs["tools"] = tools
            if system_instruction:
                kwargs["system_instruction"] = system_instruction
            self._model_cache[cache_key] = genai.GenerativeModel(model_id, **kwargs)
        return self._model_cache[cache_key]

    async def execute_task_async(
        self, prompt: str, generation_config: Optional[dict] = None, is_sensitive: bool = False,
        tools: list = None, system_instruction: str = None
    ) -> Tuple[Optional[str], str]:
        """
        Ejecuta un prompt pasando por la jerarquía. 
        Si detecta Cuota Exhausted, marca el estado degradado.
        """
        if check_is_degraded():
            rem = get_remaining_cooldown()
            logger.warning(f"[AIRouter] Sistema en MODO DEGRADADO. Faltan {rem}s.")
            return None, "degraded"

        for model_info in GEMINI_MODELS:
            model_id = model_info["id"]
            model_name = model_info["name"]
            try:
                model = self._get_model(model_id, tools, system_instruction)
                kwargs = {}
                if generation_config:
                    kwargs["generation_config"] = generation_config
                    
                response = await asyncio.to_thread(model.generate_content, prompt, **kwargs)
                return response.text, model_id
                
            except Exception as e:
                category = classify_ai_error(e)
                logger.warning(f"[AIRouter] Error en {model_name}: {category.value} - {str(e)[:100]}")
                
                if category in [AIErrorCategory.CUOTA, AIErrorCategory.BILLING]:
                    # Bloqueamos el router para no reintentar quemando cuota
                    logger.error("[AIRouter] CUOTA AGOTADA. Activando modo degradado global.")
                    write_quota_state(True)
                    return None, "quota_exhausted"
                elif category == AIErrorCategory.CLAVE_INVALIDA:
                    logger.error("[AIRouter] API KEY INVÁLIDA.")
                    return None, "invalid_key"
                # Si es otro error (RED, etc.), intenta el siguiente modelo Gemini

        # Si llegamos aquí, Gemini falló en todos sus modelos.
        # Evaluar OpenRouter si hay clave configurada y no hay datos sensibles
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key and not contains_sensitive_data(prompt, is_sensitive):
            logger.info("[AIRouter] Intentando fallback a OpenRouter...")
            try:
                import aiohttp
                import json
                headers = {
                    "Authorization": f"Bearer {openrouter_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "meta-llama/llama-3-8b-instruct:free",
                    "messages": [{"role": "user", "content": prompt}]
                }
                async with aiohttp.ClientSession() as session:
                    async with session.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data) as resp:
                        if resp.status == 200:
                            res_json = await resp.json()
                            text = res_json['choices'][0]['message']['content']
                            return text, "openrouter/llama-3-8b-free"
                        else:
                            logger.error(f"[AIRouter] OpenRouter falló con status {resp.status}")
            except Exception as e:
                logger.error(f"[AIRouter] Excepción en OpenRouter: {e}")
        else:
            if contains_sensitive_data(prompt, is_sensitive):
                logger.warning("[AIRouter] Fallback cancelado por PRIVACIDAD (datos sensibles detectados).")
            else:
                logger.debug("[AIRouter] OpenRouter no configurado.")

        return None, "exhausted"

    def execute_task_sync(
        self, prompt: str, generation_config: Optional[dict] = None, is_sensitive: bool = False,
        tools: list = None, system_instruction: str = None
    ) -> Tuple[Optional[str], str]:
        """Versión síncrona de execute_task_async."""
        if check_is_degraded():
            return None, "degraded"
            
        for model_info in GEMINI_MODELS:
            model_id = model_info["id"]
            model_name = model_info["name"]
            try:
                model = self._get_model(model_id, tools, system_instruction)
                kwargs = {}
                if generation_config:
                    kwargs["generation_config"] = generation_config
                    
                response = model.generate_content(prompt, **kwargs)
                return response.text, model_id
                
            except Exception as e:
                category = classify_ai_error(e)
                logger.warning(f"[AIRouter] Error en {model_name} (sync): {category.value}")
                
                if category in [AIErrorCategory.CUOTA, AIErrorCategory.BILLING]:
                    write_quota_state(True)
                    return None, "quota_exhausted"
                elif category == AIErrorCategory.CLAVE_INVALIDA:
                    return None, "invalid_key"

        # Sync fallback to OpenRouter
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key and not contains_sensitive_data(prompt, is_sensitive):
            try:
                import requests
                headers = {
                    "Authorization": f"Bearer {openrouter_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "meta-llama/llama-3-8b-instruct:free",
                    "messages": [{"role": "user", "content": prompt}]
                }
                resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
                if resp.status_code == 200:
                    return resp.json()['choices'][0]['message']['content'], "openrouter/llama-3-8b-free"
            except Exception as e:
                logger.error(f"[AIRouter] Excepción sync en OpenRouter: {e}")

        return None, "exhausted"

    async def analyze_multimodal_async(
        self, prompt: str, file_bytes: bytes, mime_type: str, generation_config: Optional[dict] = None
    ) -> Tuple[Optional[str], str]:
        """Versión multimodal asíncrona."""
        if check_is_degraded():
            return None, "degraded"
            
        for model_info in GEMINI_MODELS:
            model_id = model_info["id"]
            try:
                model = self._get_model(model_id)
                content = [prompt, {"mime_type": mime_type, "data": file_bytes}]
                kwargs = {}
                if generation_config:
                    kwargs["generation_config"] = generation_config
                    
                response = await asyncio.to_thread(model.generate_content, content, **kwargs)
                return response.text, model_id
                
            except Exception as e:
                category = classify_ai_error(e)
                if category in [AIErrorCategory.CUOTA, AIErrorCategory.BILLING]:
                    write_quota_state(True)
                    return None, "quota_exhausted"
                    
        return None, "exhausted"

# Instancia Global
global_router = AIRouter()

# Funciones de conveniencia compatibles
async def generate_ai_response(prompt: str, generation_config: Optional[dict] = None, is_sensitive: bool = False) -> str:
    text, model_id = await global_router.execute_task_async(prompt, generation_config, is_sensitive)
    if not text:
        return "Koal-AI: Servicio temporalmente limitado (Modo Degradado)."
    return text

def generate_ai_response_sync(prompt: str, generation_config: Optional[dict] = None, is_sensitive: bool = False) -> str:
    text, model_id = global_router.execute_task_sync(prompt, generation_config, is_sensitive)
    if not text:
        return "Koal-AI: Servicio temporalmente limitado (Modo Degradado)."
    return text
