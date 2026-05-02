import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.models import Pedido, Producto, YieldRule, ESGMétrics
from backend.utils.logger import logger

class AOIEngine:
    """
    Advanced Operations Intelligence (AOI) Engine V9.2.
    Predicts sales, suggests price adjustments, and monitors ESG impact.
    """
    
    @staticmethod
    def predict_sales_next_24h(db: Session) -> dict:
        """
        Simula una predicción basada en datos históricos y reglas de Yield.
        """
        # Obtenemos la última regla de Yield activa
        yield_rule = db.query(YieldRule).filter_by(is_active=True).first()
        multiplier = 1.0 + (yield_rule.ajuste_precio_pct / 100) if yield_rule else 1.0
        
        # Simulación de predicción estocástica
        base_prediction = 1500.0 # Ventas base
        predicted_revenue = round(base_prediction * multiplier * (0.9 + random.random() * 0.2), 2)
        confidence = 85.0 + random.random() * 10
        
        return {
            "predicted_revenue": predicted_revenue,
            "multiplier_applied": multiplier,
            "confidence_score": round(confidence, 1),
            "factors": ["Yield Rule Active", "Historical Saturday Trend", "Weather Forecast (Cloudy)"]
        }

    @staticmethod
    def get_esg_impact_summary(db: Session) -> dict:
        """
        Calcula el impacto ambiental acumulado.
        """
        metrics = db.query(ESGMétrics).order_by(ESGMétrics.fecha.desc()).first()
        if not metrics:
            return {"status": "No data available"}
            
        return {
            "co2_saved_kg": metrics.co2_saved_kg,
            "food_waste_saved_kg": metrics.food_waste_kg,
            "plastic_removed_kg": metrics.plastic_reduced_kg,
            "rating": "A++ Sustainable"
        }

    @staticmethod
    def get_menu_optimization_tips(db: Session) -> list:
        """
        Sugiere cambios en el menú basados en la matriz de ingeniería.
        """
        # Mock logic representing the Boston Matrix analysis
        return [
            {"product": "Pollo a l'ast", "action": "Promote (Star)", "reason": "High margin, High volume"},
            {"product": "Patatas Coraje", "action": "Re-engineer (Puzzle)", "reason": "High margin, Low volume"},
            {"product": "Ensaladilla Rusa", "action": "Remove (Dog)", "reason": "Low margin, Low volume"}
        ]
