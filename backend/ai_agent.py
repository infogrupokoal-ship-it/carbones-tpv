"""
Koal-AI Agent - Motor de Inteligencia Operacional
===================================================
Usa AIModelManager para rotación automática de modelos Gemini.
Modelo primario: gemini-2.5-pro → fallback automático si hay errores de cuota.
"""

import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import Producto, Pedido, Ingrediente
from .config import settings
from .database import SessionLocal
from .utils.ai_model_manager import ai_manager, generate_ai_response
from .utils.logger import logger


def get_menu_text(db: Session) -> str:
    """Genera una representación técnica del inventario para la IA."""
    try:
        productos = db.query(Producto).all()
        menu_lines = [
            f"- {p.nombre}: {p.precio}€ (Stock: {p.stock_actual})"
            for p in productos
        ]
        return "\n".join(menu_lines) if menu_lines else "Sin productos disponibles."
    except Exception as e:
        logger.error(f"[AI Agent] Error obteniendo menú: {e}")
        return "Error al obtener el catálogo."


def get_business_summary(db: Session) -> str:
    """Calcula métricas clave de rendimiento en tiempo real."""
    try:
        today = datetime.date.today()
        ventas_hoy = (
            db.query(func.sum(Pedido.total))
            .filter(func.date(Pedido.fecha) == today)
            .scalar() or 0.0
        )
        num_pedidos = (
            db.query(Pedido)
            .filter(func.date(Pedido.fecha) == today)
            .count()
        )
        bajo_minimo = (
            db.query(Ingrediente)
            .filter(Ingrediente.stock_actual <= Ingrediente.stock_minimo)
            .all()
        )
        nombres_bajo_minimo = (
            ", ".join([i.nombre for i in bajo_minimo])
            if bajo_minimo
            else "Nivel de Stock Óptimo"
        )

        return f"""
    MÉTRICAS OPERATIVAS ({today}):
    - Ingresos Brutos: {ventas_hoy:.2f}€
    - Volumen de Pedidos: {num_pedidos}
    - Alertas de Suministro: {nombres_bajo_minimo}
    - Modelo IA Activo: {ai_manager.current_model_info['name']}
        """
    except Exception as e:
        logger.error(f"[AI Agent] Error obteniendo métricas: {e}")
        return f"Error al obtener métricas operativas: {e}"


async def ask_asador_ai(prompt: str, user_role: str = "admin") -> str:
    """
    Consultoría estratégica impulsada por IA con contexto operativo inyectado.
    Usa rotación automática de modelos: gemini-2.5-pro → 2.0-flash → 2.0-flash-lite → 1.5-pro
    """
    if not settings.GOOGLE_API_KEY:
        return "Koal-AI: El servicio no está configurado (Falta GOOGLE_API_KEY)."

    db = SessionLocal()
    try:
        business_data = get_business_summary(db)
        menu_data = get_menu_text(db)
        model_status = ai_manager.get_status()

        import os
        global_prompt = ""
        prompt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "GLOBAL_AI_OPERATING_PROMPT.md")
        try:
            if os.path.exists(prompt_path):
                with open(prompt_path, "r", encoding="utf-8") as f:
                    global_prompt = f.read()
        except Exception:
            pass

        full_prompt = f"""
        Eres 'Koal-AI', el sistema de inteligencia operacional de Carbones y Pollos.
        Actúas como un Gerente de Operaciones Senior (COO) virtual.
        
        SITUACIÓN ACTUAL DEL NEGOCIO:
        {business_data}
        
        INVENTARIO Y CARTA:
        {menu_data}
        
        REQUERIMIENTO DEL USUARIO ({user_role}): {prompt}
        
        PROTOCOLO DE ORQUESTACIÓN Y COMUNICACIÓN (REGLAS MAESTRAS DE JORGE):
        {global_prompt}
        
        PROTOCOLO DE RESPUESTA Y RESTRICCIONES CRÍTICAS:
        1. Lenguaje ejecutivo, conciso y orientado a la acción.
        2. Prioriza la rentabilidad y la eficiencia de stock.
        3. Si detectas anomalías en los datos, notifícalo inmediatamente.
        4. No inventes métricas financieras no proporcionadas.
        5. Estás estrictamente limitado a analizar y basar tus respuestas en el INVENTARIO Y CARTA proporcionado. No asumas ni inventes productos, stocks o datos financieros bajo ninguna circunstancia.
        6. Si el usuario pregunta qué modelo IA estás usando, responde: {model_status['active_model']}
        """

        response = await generate_ai_response(full_prompt)
        return response

    except Exception as e:
        logger.error(f"[AI Agent] Error crítico: {e}")
        return f"Error de Inteligencia Operativa: {str(e)}"
    finally:
        db.close()
