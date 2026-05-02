import random
from typing import Dict

class YieldPricingEngine:
    """
    Dynamic Yield Pricing Engine.
    Adjusts product prices based on demand, stock levels, and environmental factors.
    """
    
    def __init__(self):
        self.factors = {
            "demand": 1.0,
            "stock_scarcity": 1.0,
            "weather_impact": 1.0,
            "time_bonus": 1.0
        }

    def calculate_surge_multiplier(self) -> float:
        # Simulate real-time calculation
        self.factors["demand"] = 1.0 + (random.random() * 0.2)
        self.factors["stock_scarcity"] = 1.0 + (random.random() * 0.1)
        self.factors["weather_impact"] = 0.95 if random.random() < 0.2 else 1.0 # Rain discount?
        
        multiplier = 1.0
        for f in self.factors.values():
            multiplier *= f
        return round(multiplier, 3)

    def get_market_insights(self) -> Dict:
        return {
            "multiplier": self.calculate_surge_multiplier(),
            "active_factors": self.factors,
            "sentiment": "BULLISH" if self.factors["demand"] > 1.1 else "STABLE",
            "next_adjustment": "15m"
        }

# Global Instance
yield_engine = YieldPricingEngine()
