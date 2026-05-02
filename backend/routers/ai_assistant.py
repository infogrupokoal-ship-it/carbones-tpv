"""
AI Assistant Router - Asistente de Ventas Koal-AI
====================================================
Usa AIModelManager para rotación automática de modelos Gemini.
Endpoint: POST /api/ai/chat
"""
import os
import psutil
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Producto
from ..config import settings
from ..utils.logger import logger
from ..utils.ai_model_manager import ai_manager
from .admin_audit import log_audit_action

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


class ChatRequest(BaseModel):
    message: str
    context: dict = {}


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

        # Telemetría en tiempo real para el contexto de la IA
        process = psutil.Process(os.getpid())
        system_context = {
            "version": settings.APP_VERSION,
            "cpu_usage": f"{psutil.cpu_percent()}%",
            "memory_usage": f"{psutil.virtual_memory().percent}%",
            "process_rss": f"{process.memory_info().rss / 1024 / 1024:.2f} MB",
            "db_status": "ONLINE"
        }

        system_prompt = f"""
        Eres "Carbonito", el asistente gourmet de Carbones y Pollos.
        Tu objetivo es ayudar a los clientes a elegir su comida y AUMENTAR LAS VENTAS.
        
        SISTEMA (UEOS V11.0):
        - Estado: {system_context['db_status']}
        - Carga CPU: {system_context['cpu_usage']}
        - RAM: {system_context['memory_usage']}
        - Versión: {system_context['version']}

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
            f"Contexto del Sistema (Ruta): {req.context.get('path', 'n/a')}\n"
            f"Contexto del Sistema (Módulo): {req.context.get('module', 'n/a')}"
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

class NLPRequest(BaseModel):
    text: str

@router.post("/nlp-parse")
async def parse_order_nlp(req: NLPRequest, db: Session = Depends(get_db)):
    """
    Fase 7: Parsing de pedidos en lenguaje natural (NLP).
    Extrae la intención de compra y las cantidades de un texto no estructurado.
    """
    if not settings.GOOGLE_API_KEY:
        raise HTTPException(status_code=503, detail="AI no configurada")
        
    try:
        productos = db.query(Producto).all()
        nombres_prods = ", ".join([p.nombre for p in productos])
        
        system_prompt = f"""
        Eres un asistente de parsing de pedidos para Carbones y Pollos.
        Extrae los productos mencionados en el texto del usuario y devuelve un JSON estricto.
        
        Productos disponibles: {nombres_prods}
        
        El JSON debe ser un array de objetos con las claves: "producto" (el nombre más cercano) y "cantidad" (número entero).
        Ejemplo: [{{"producto": "Pollo Asado", "cantidad": 2}}]
        No devuelvas nada de texto, solo JSON.
        """
        
        full_prompt = f"{system_prompt}\nTexto: {req.text}"
        
        reply_text, _ = await ai_manager.generate_content_async(full_prompt)
        
        if not reply_text:
            raise ValueError("Respuesta vacía del modelo IA")
            
        # Limpiar backticks del markdown de código (```json ... ```) si existen
        clean_json = reply_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        
        import json
        parsed = json.loads(clean_json)
        
        return {"status": "success", "parsed_items": parsed}
    except Exception as e:
        logger.error(f"Error NLP: {e}")
        return {"status": "error", "message": "No se pudo entender el pedido", "raw": str(e)}
