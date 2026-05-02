import google.generativeai as genai
from backend.config import settings
from backend.routers import stats
from sqlalchemy.orm import Session
import json

class BusinessAIAgent:
    """
    Fase 32: Agente de Inteligencia de Negocio (BI AI).
    Analiza métricas en tiempo real y sugiere decisiones estratégicas al gerente.
    """
    
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def get_strategic_briefing(self, db: Session) -> str:
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
            return response.text
        except Exception as e:
            return f"Error en análisis IA: {str(e)}"
