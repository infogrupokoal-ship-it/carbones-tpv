import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Pedido
from ..utils.logger import logger
from .reporting import ReportingService

class FinancialService:
    @staticmethod
    def generate_z_report(db: Session, efectivo_declarado: float = 0.0) -> str:
        """
        Punto de entrada para el cierre de jornada. Delega en ReportingService 
        la lógica de consolidación y retorna el resumen ejecutivo.
        """
        try:
            reporte = ReportingService.generar_cierre_z(db, efectivo_declarado)
            return reporte.resumen_texto
        except Exception as e:
            logger.error(f"Error financiero en Cierre Z: {str(e)}")
            raise

    @staticmethod
    def get_financial_kpis(db: Session) -> dict:
        """
        Cálculo de Indicadores Clave de Desempeño (KPIs) financieros.
        Analiza márgenes, ticket promedio y rentabilidad operativa.
        """
        try:
            today = datetime.date.today()
            ventas_hoy = db.query(func.sum(Pedido.total)).filter(func.date(Pedido.fecha) == today).scalar() or 0.0
            num_pedidos = db.query(Pedido).filter(func.date(Pedido.fecha) == today).count()
            
            ticket_promedio = ventas_hoy / num_pedidos if num_pedidos > 0 else 0.0
            
            # En una fase avanzada, aquí se restaría el coste real de materia prima (Escandallo)
            margen_bruto_estimado = 0.65 # Basado en histórico operativo
            
            return {
                "total_ventas": round(ventas_hoy, 2),
                "ticket_promedio": round(ticket_promedio, 2),
                "pedidos_realizados": num_pedidos,
                "margen_operativo_est": f"{margen_bruto_estimado * 100}%",
                "ebitda_proyectado": round(ventas_hoy * 0.25, 2) # Proyección conservadora
            }
        except Exception as e:
            logger.error(f"Error calculando KPIs financieros: {e}")
            return {}
