# backend/ai/gemini_provider.py
import os
import logging

class GeminiProvider:
    def __init__(self, model_name="gemini-1.5-flash", timeout=30):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.model_name = model_name
        self.timeout = timeout
        
    def ask(self, prompt, context=""):
        if not self.api_key:
            logging.error("GEMINI_API_KEY no encontrada.")
            return "Error: API Key missing."
        # Placeholder para llamar a google.generativeai
        return f"Simulando respuesta de {self.model_name}..."

    def ask_json(self, prompt, schema):
        # Placeholder para Structured JSON Output
        return "{}"
