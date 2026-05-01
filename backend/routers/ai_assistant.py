from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Producto, Categoria
from ..config import settings
from ..utils.logger import logger

router = APIRouter(prefix="/api/ai", tags=["AI Assistant"])

# Configuración de Gemini desde settings
if settings.GOOGLE_API_KEY:
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    model = None
    logger.warning("⚠️ AI_ASSISTANT: GOOGLE_API_KEY no configurada. El asistente estará desactivado.")

class ChatRequest(BaseModel):
    message: str
    context: str = ""

@router.post("/chat")
async def chat_with_assistant(req: ChatRequest, db: Session = Depends(get_db)):
    """
    Asistente de Ventas IA: Ayuda al usuario a elegir su menú y ofrece recomendaciones.
    """
    if not model:
        return {"reply": "Lo siento, el asistente no está disponible en este momento. 🔥", "agent": "Carbonito"}
        
    try:
        # 1. Obtener catálogo para contexto
        productos = db.query(Producto).all()
        menu_text = "\n".join([f"- {p.nombre}: {p.precio}€" for p in productos])
        
        system_prompt = f"""
        Eres "Carbonito", el asistente gourmet de Carbones y Pollos. 
        Tu objetivo es ayudar a los clientes a elegir su comida y AUMENTAR LAS VENTAS ofreciendo complementos.
        
        MENÚ ACTUAL:
        {menu_text}
        
        REGLAS:
        1. Sé amable, divertido y profesional. Usa emojis relacionados con comida.
        2. Si eligen un pollo, recomienda patatas o ensalada.
        3. Si eligen una pizza, recomienda bebidas o postre.
        4. Si preguntan por el precio, dáselo exacto según el menú.
        5. Mantén las respuestas breves y directas.
        6. Responde siempre en Español.
        """
        
        full_prompt = f"{system_prompt}\n\nMensaje del cliente: {req.message}\nContexto adicional: {req.context}"
        
        response = model.generate_content(full_prompt)
        
        return {
            "reply": response.text,
            "agent": "Carbonito"
        }
    except Exception as e:
        logger.error(f"Error AI Assistant: {e}")
        return {
            "reply": "Lo siento, estoy avivando las brasas ahora mismo. ¿Puedo ayudarte con otra cosa? 🔥",
            "agent": "Carbonito"
        }
