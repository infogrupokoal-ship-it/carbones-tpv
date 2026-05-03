import random
from datetime import datetime, timedelta, UTC
from sqlalchemy.orm import Session

class AIBIEngine:
    """
    Motor de análisis proactivo que genera 'Neural Insights' para el dashboard administrativo.
    Simula el análisis de tendencias y optimización de recursos.
    """

    @staticmethod
    def get_proactive_insights(db: Session):
        insights = []
        
        # Simulación de análisis de demanda
        hour = datetime.now(UTC).hour
        if 13 <= hour <= 15 or 20 <= hour <= 22:
            insights.append({
                "id": "DEMAND_PEAK",
                "level": "CRITICAL",
                "message": "Pico de demanda detectado. Se recomienda activar protocolo de prep extra para Pollos Asados.",
                "action_cta": "Ver KDS",
                "timestamp": datetime.now(UTC).isoformat()
            })
        
        # Simulación de análisis de stock/merma
        insights.append({
            "id": "STOCK_OPT",
            "level": "INFO",
            "message": "Optimización de inventario: Se detecta excedente de Patatas Fritas. Recomendado: Menú Promo 'Combo Crujiente'.",
            "action_cta": "Editar Menú",
            "timestamp": datetime.now(UTC).isoformat()
        })

        # Simulación de eficiencia logística
        insights.append({
            "id": "FLEET_EFF",
            "level": "SUCCESS",
            "message": "Eficiencia de reparto al 98%. 3 repartidores en ruta óptima.",
            "action_cta": "Ver Mapa",
            "timestamp": (datetime.now(UTC) - timedelta(minutes=5)).isoformat()
        })

        return insights

    @staticmethod
    def generate_system_health():
        return {
            "neural_load": random.randint(15, 45),
            "database_latency": f"{random.uniform(2, 8):.2f}ms",
            "active_nodes": random.randint(12, 18),
            "uptime": "99.998%"
        }
