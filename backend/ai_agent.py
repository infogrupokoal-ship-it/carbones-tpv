import datetime
import asyncio
import google.generativeai as genai
from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import Producto, Pedido, Ingrediente
from .config import settings
from .database import SessionLocal

# Configuración Profesional de Gemini
if settings.GOOGLE_API_KEY:
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    model = None

def get_menu_text(db: Session):
    """Genera una representación técnica del inventario para la IA."""
    productos = db.query(Producto).all()
    menu_lines = [f"- {p.nombre}: {p.precio}€ (Stock: {p.stock_actual})" for p in productos]
    return "\n".join(menu_lines)

def get_business_summary(db: Session):
    """Calcula métricas clave de rendimiento en tiempo real."""
    today = datetime.date.today()
    
    # Ventas agregadas de hoy
    ventas_hoy = db.query(func.sum(Pedido.total)).filter(func.date(Pedido.fecha) == today).scalar() or 0.0
    num_pedidos = db.query(Pedido).filter(func.date(Pedido.fecha) == today).count()
    
    # Análisis de Materia Prima
    bajo_minimo = db.query(Ingrediente).filter(Ingrediente.stock_actual <= Ingrediente.stock_minimo).all()
    nombres_bajo_minimo = ", ".join([i.nombre for i in bajo_minimo]) if bajo_minimo else "Nivel de Stock Óptimo"
    
    return f"""
    MÉTRICAS OPERATIVAS ({today}):
    - Ingresos Brutos: {ventas_hoy:.2f}€
    - Volumen de Pedidos: {num_pedidos}
    - Alertas de Suministro: {nombres_bajo_minimo}
    """

async def ask_asador_ai(prompt: str, user_role: str = "admin"):
    """Consultoría estratégica impulsada por IA con contexto operativo inyectado."""
    if not model:
        return "Koal-AI: El servicio no está configurado (Falta GOOGLE_API_KEY)."
        
    db = SessionLocal()
    try:
        business_data = get_business_summary(db)
        menu_data = get_menu_text(db)
        
        full_prompt = f"""
        Eres 'Koal-AI', el sistema de inteligencia operacional de Carbones y Pollos.
        Actúas como un Gerente de Operaciones Senior (COO) virtual.
        
        SITUACIÓN ACTUAL DEL NEGOCIO:
        {business_data}
        
        INVENTARIO Y CARTA:
        {menu_data}
        
        REQUERIMIENTO DEL USUARIO ({user_role}): {prompt}
        
        PROTOCOLO DE RESPUESTA:
        1. Lenguaje ejecutivo, conciso y orientado a la acción.
        2. Prioriza la rentabilidad y la eficiencia de stock.
        3. Si detectas anomalías en los datos, notifícalo inmediatamente.
        4. No inventes métricas financieras no proporcionadas.
        """
        
        # Ejecución asíncrona simulada (el SDK de Gemini es síncrono por defecto)
        response = await asyncio.to_thread(model.generate_content, full_prompt)
        return response.text
    except Exception as e:
        return f"Error de Inteligencia Operativa: {str(e)}"
    finally:
        db.close()
