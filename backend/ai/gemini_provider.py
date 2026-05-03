# backend/ai/gemini_provider.py
import os
import logging
import asyncio
import google.generativeai as genai

logger = logging.getLogger(__name__)

class GeminiProvider:
    def __init__(self, model_name=None, timeout=30, system_instruction=None, response_mime_type="text/plain"):
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.model_name = model_name or os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
        self.timeout = timeout
        self.system_instruction = system_instruction
        self.response_mime_type = response_mime_type
        if self.api_key:
            genai.configure(api_key=self.api_key)
        else:
            logger.warning("GEMINI_API_KEY o GOOGLE_API_KEY no encontrada.")

    async def ask_async(self, prompt, context="", temp=0.2):
        if not self.api_key:
            logger.error("API Key missing.")
            return "Error: API Key missing."
            
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=genai.GenerationConfig(
                    temperature=temp,
                    response_mime_type=self.response_mime_type
                ),
                system_instruction=self.system_instruction
            )
            # Run in a thread to avoid blocking the event loop since generate_content can be synchronous if not using async client properly
            # Or use generate_content_async if available
            if hasattr(model, 'generate_content_async'):
                 response = await asyncio.wait_for(model.generate_content_async(full_prompt), timeout=self.timeout)
            else:
                 response = await asyncio.to_thread(model.generate_content, full_prompt)
                 
            return response.text
        except Exception as e:
            logger.error(f"Error en GeminiProvider.ask_async: {e}")
            return f"Error en la generación: {str(e)}"

    def ask(self, prompt, context="", temp=0.2):
        # Sync version for simplicity in scripts
        if not self.api_key:
            return "Error: API Key missing."
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=genai.GenerationConfig(temperature=temp)
            )
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error en GeminiProvider.ask: {e}")
            return f"Error en la generación: {str(e)}"
