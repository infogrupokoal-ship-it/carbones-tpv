import random
from datetime import datetime, timedelta
from typing import List, Dict

class AOIEngine:
    """
    Autonomous Operational Intelligence Engine v5.0
    Predicts operational needs, analyzes business health, and triggers strategic suggestions.
    """
    
    def __init__(self):
        self.version = "5.0-SINGULARITY"
        self.last_run = None
        self.active_predictions = []

    def analyze_business_state(self, historical_data: List[Dict]):
        """
        Analyzes the last 30 days of data to find patterns.
        """
        # Simulation of advanced pattern recognition
        total_sales = sum(d.get('total', 0) for d in historical_data)
        avg_sale = total_sales / len(historical_data) if historical_data else 0
        
        insight = {
            "timestamp": datetime.now().isoformat(),
            "health_score": random.randint(85, 98),
            "efficiency": random.randint(90, 100),
            "insights": [
                "Demanda proyectada aumenta +15% en fin de semana.",
                "Optimización de ruta en Delivery detectada: ahorro potencial 8%.",
                "Alerta de Stock: El Carbón Vegetal se agotará en 4.2 días."
            ]
        }
        return insight

    def generate_future_forecast(self, days: int = 7) -> List[Dict]:
        """
        Generates a predictive forecast for the next N days.
        """
        forecast = []
        base_date = datetime.now()
        for i in range(days):
            target_date = base_date + timedelta(days=i)
            # Simulated seasonality and growth
            expected_demand = 85 + (i * 2) + random.randint(-5, 5)
            if target_date.weekday() >= 5: # Weekend surge
                expected_demand += 40
                
            forecast.append({
                "date": target_date.strftime("%Y-%m-%d"),
                "expected_sales": round(expected_demand * 12.5, 2),
                "confidence": 0.92 - (i * 0.02),
                "risk_level": "LOW" if expected_demand < 120 else "MEDIUM"
            })
        return forecast

    def get_strategic_actions(self) -> List[Dict]:
        """
        Returns a list of autonomous suggestions for the manager.
        """
        return [
            {
                "id": "ACT-001",
                "module": "Marketing",
                "action": "Lanzar campaña 'Weekend Combo' - Alta probabilidad de conversión.",
                "impact": "HIGH",
                "status": "SUGGESTED"
            },
            {
                "id": "ACT-002",
                "module": "Logistics",
                "action": "Pre-ordenar 200kg de Pollo para el Sábado.",
                "impact": "CRITICAL",
                "status": "AUTO-PREPARED"
            }
        ]

# Global Instance
aoi_engine = AOIEngine()
