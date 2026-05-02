"""
AI Assistant Router - Asistente de Ventas Koal-AI
====================================================
Usa AIModelManager para rotación automática de modelos Gemini.
Endpoint: POST /api/ai/chat
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Producto
from ..config import settings
from ..utils.logger import logger
from ..utils.ai_model_manager import ai_manager

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


class ChatRequest(BaseModel):
    message: str
    context: str = ""


class ChatResponse(BaseModel):
    reply: str
    agent: str
    model_used: str
    model_tier: str


@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(req: ChatRequest, db: Session = Depends(get_db)):
    """
    Asistente de Ventas IA: Ayuda al usuario a elegir su menú y ofrece recomendaciones.
    Usa rotación automática de modelos con fallback inteligente.
    """
    if not settings.GOOGLE_API_KEY:
        return ChatResponse(
            reply="Lo siento, el asistente Carbonito requiere una Google API Key para funcionar. Por favor, configúrala en el panel de control. 🔥",
            agent="Carbonito",
            model_used="OFFLINE",
            model_tier="NONE"
        )

    try:
        productos = db.query(Producto).all()
        menu_text = "\n".join([f"- {p.nombre}: {p.precio}€" for p in productos])

        system_prompt = f"""
        Eres "Carbonito", el asistente gourmet de Carbones y Pollos.
        Tu objetivo es ayudar a los clientes a elegir su comida y AUMENTAR LAS VENTAS.

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

        full_prompt = (
            f"{system_prompt}\n\n"
            f"Mensaje del cliente: {req.message}\n"
            f"Contexto adicional: {req.context}"
        )

        reply_text, model_used = await ai_manager.generate_content_async(full_prompt)

        if reply_text is None:
            reply_text = "Lo siento, estoy avivando las brasas ahora mismo. ¿Puedo ayudarte con otra cosa? 🔥"

        final_model_info = ai_manager.current_model_info
        return ChatResponse(
            reply=reply_text,
            agent="Carbonito",
            model_used=final_model_info["id"],
            model_tier=final_model_info["tier"]
        )

    except Exception as e:
        logger.error(f"[AI Assistant] Error crítico: {e}")
        return ChatResponse(
            reply="Lo siento, estoy avivando las brasas ahora mismo. ¿Puedo ayudarte con otra cosa? 🔥",
            agent="Carbonito",
            model_used="error",
            model_tier="ERROR"
        )


@router.get("/status")
async def get_ai_status():
    """
    Devuelve el estado completo del gestor de modelos IA.
    Incluye modelo activo, tiempo para reset al primario, y jerarquía completa.
    """
    return {
        "status": "operational",
        **ai_manager.get_status()
    }
