"""
AI Assistant Router - Asistente de Ventas Carbones y Pollos
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
from ..models import Producto, LogOperativo
from ..config import settings
from ..utils.logger import logger
from ..shared_ai.ai_router import global_router
from ..shared_ai.ai_task_lock import check_is_degraded, get_remaining_cooldown

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

        # Telemetría en tiempo real y logs operativos para la IA
        process = psutil.Process(os.getpid())
        recent_logs = db.query(LogOperativo).order_by(LogOperativo.fecha.desc()).limit(10).all()
        logs_text = "\n".join([f"[{log_entry.fecha.strftime('%H:%M')}] {log_entry.modulo}: {log_entry.mensaje}" for log_entry in recent_logs])

        system_context = {
            "version": settings.APP_VERSION,
            "cpu_usage": f"{psutil.cpu_percent()}%",
            "memory_usage": f"{psutil.virtual_memory().percent}%",
            "process_rss": f"{process.memory_info().rss / 1024 / 1024:.2f} MB",
            "db_status": "ONLINE",
            "logs": logs_text
        }

        system_prompt = f"""
        Eres "Carbonito", el asistente gourmet de Carbones y Pollos.
        Tu objetivo es ayudar a los clientes a elegir su comida y AUMENTAR LAS VENTAS.
        
        SISTEMA (UEOS V11.0):
        - Estado: {system_context['db_status']}
        - Carga CPU: {system_context['cpu_usage']}
        - RAM: {system_context['memory_usage']}
        - Versión: {system_context['version']}

        LOGS RECIENTES:
        {system_context['logs'] if system_context['logs'] else "No hay alertas recientes."}

        MENÚ ACTUAL:
        {menu_text}

        REGLAS Y RESTRICCIONES CRÍTICAS:
        1. Sé amable, divertido y profesional. Usa emojis relacionados con comida.
        2. Si eligen un pollo, recomienda patatas o ensalada (solo si están en el menú).
        3. BAJO NINGUNA CIRCUNSTANCIA inventes productos, modificadores o precios que no estén explícitamente listados en el MENÚ ACTUAL.
        4. Si preguntan por el precio, dáselo exacto según el MENÚ ACTUAL. Nunca ofrezcas precios distintos.
        5. Si el cliente pide algo que no está en el menú, discúlpate e indica amablemente que no disponemos de ese artículo, ofreciendo una alternativa real del menú.
        6. Mantén las respuestas breves y directas.
        7. Responde siempre en Español.
        
        COMUNICACIÓN CON OTROS AGENTES (SISTEMA DE MENSAJERÍA AGENTE):
        - Si detectas un error crítico (500, fallo de DB en logs), o si el usuario te pide algo técnico que no puedes hacer (ej: "reinicia el servidor", "revisa los logs de ayer"), puedes solicitar ayuda al agente "OPENCLAW" (DevOps).
        - Para hacerlo, tu respuesta debe incluir al final (en una línea aparte) el comando: [[AGENT_REQUEST: OPENCLAW | Tarea: [Descripción detallada de la tarea]]]
        - No abuses de esto, solo para tareas técnicas fuera de tu alcance.
        """

        full_prompt = (
            f"{system_prompt}\n\n"
            f"Mensaje del cliente: {req.message}\n"
            f"Contexto del Sistema (Ruta): {req.context.get('path', 'n/a')}\n"
            f"Contexto del Sistema (Módulo): {req.context.get('module', 'n/a')}"
        )

        reply_text, model_used = await global_router.execute_task_async(full_prompt)

        if reply_text is None:
            reply_text = "Lo siento, estoy avivando las brasas ahora mismo. ¿Puedo ayudarte con otra cosa? 🔥"
            
        final_model_info = {
            "id": model_used,
            "tier": "fallback" if "openrouter" in model_used or model_used in ["exhausted", "degraded"] else "primary"
        }
        
        # --- NUEVO: Interceptación de AgentMessage (Industrialización) ---
        if "[[AGENT_REQUEST:" in reply_text:
            try:
                import json
                from ..models import AgentMessage # Asumiendo que está en models.py
                
                # Extraer la tarea
                parts = reply_text.split("[[AGENT_REQUEST:")[1].split("]]")[0].split("|")
                target = parts[0].strip()
                task_desc = parts[1].replace("Tarea:", "").strip() if len(parts) > 1 else "Tarea no especificada"
                
                new_agent_msg = AgentMessage(
                    sender="CARBONITO_TPV",
                    receiver=target,
                    message_type="task_delegation",
                    payload=json.dumps({"task": task_desc, "context": system_context}),
                    status="pending"
                )
                db.add(new_agent_msg)
                db.commit()
                logger.info(f"[AI Assistant] Delegada tarea a {target}: {task_desc}")
            except Exception as msg_err:
                logger.error(f"[AI Assistant] Error al registrar AgentMessage: {msg_err}")

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
    is_degraded = check_is_degraded()
    rem_cooldown = get_remaining_cooldown() if is_degraded else 0
    return {
        "status": "degraded" if is_degraded else "operational",
        "current_model": "openrouter/llama-3-8b-free" if is_degraded else "gemini-2.5-pro",
        "is_fallback": is_degraded,
        "cooldown_remaining": rem_cooldown
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
        
        reply_text, _ = await global_router.execute_task_async(full_prompt)
        
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
