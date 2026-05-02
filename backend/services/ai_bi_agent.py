import google.generativeai as genai
from backend.config import settings
from backend.routers import stats
from sqlalchemy.orm import Session
from backend.utils.logger import logger
import json

class BusinessAIAgent:
    """
    Fase 32: Agente de Inteligencia de Negocio (BI AI).
    Analiza métricas en tiempo real y sugiere decisiones estratégicas al gerente.
    """
    
    def __init__(self):
        if settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    async def get_strategic_briefing(self, db: Session) -> tuple[bool, str]:
        if not self.model:
            return False, "AI Model not configured (Missing API Key)."

        # Extraer métricas reales
        metrics = stats.get_sales_metrics(db)
        stock_alerts = stats.get_inventory_status(db)
        
        prompt = f"""
        Eres el COO Digital de 'Carbones y Pollos La Granja'. 
        Analiza estos datos y dame 3 acciones críticas para hoy:
        Métricas: {json.dumps(metrics)}
        Stock Crítico: {json.dumps(stock_alerts)}
        
        Responde en formato profesional, directo y orientado a maximizar el ROI.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return True, response.text
        except Exception as e:
            logger.error(f"AI Strategic Analysis Error: {e}")
            return False, str(e)

    async def analyze_and_notify(self, db: Session):
        """
        Analiza la situación y genera una notificación estratégica solo si el análisis es exitoso.
        Las notificaciones técnicas de error solo van al log.
        """
        success, brief = await self.get_strategic_briefing(db)
        
        if not success:
            return None # No notificar errores técnicos a la UI

        # Inyectar notificación en el sistema (Solo visible para ADMINS)
        from backend.routers.notifications import create_notification, Notification
        from datetime import datetime
        import uuid
        
        notif = Notification(
            id=str(uuid.uuid4()),
            title="🎯 Sugerencia IA Estratégica",
            message=brief[:250] + "...",
            type="info",
            timestamp=datetime.now(),
            module="AI Analyst",
            scope="ADMIN" # <--- Solo el jefe/admin debe ver esto
        )
        
        from backend.routers.notifications import NOTIFICATIONS_STORE
        NOTIFICATIONS_STORE.insert(0, notif.dict())
        
        return brief
