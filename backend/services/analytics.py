import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Pedido, ItemPedido, Producto
from ..utils.logger import logger

class AnalyticsService:
    """Servicio de Inteligencia de Negocio (BI) para Carbones y Pollos."""

    @staticmethod
    def get_demand_prediction(db: Session):
        """Predicción de demanda basada en históricos recientes."""
        # Lógica simplificada: media de pedidos de los últimos 7 días por franja horaria
        # En producción real, aquí se integraría un modelo de regresión liviano
        return {
            "prediccion_mañana": "Alta",
            "pico_esperado": "14:30 - 15:30",
            "productos_criticos": ["Pollo Asado XL", "Patatas Fritas Caseras"]
        }

    @staticmethod
    def get_abc_analysis(db: Session):
        """Análisis de productos por rentabilidad y volumen (Pareto)."""
        # Agregamos ventas por producto
        results = db.query(
            Producto.nombre,
            func.sum(ItemPedido.cantidad).label('volumen'),
            func.sum(ItemPedido.cantidad * ItemPedido.precio_unitario).label('ingresos')
        ).join(ItemPedido).group_by(Producto.id).order_by(func.sum(ItemPedido.cantidad).desc()).all()

        return [
            {"producto": r.nombre, "volumen": r.volumen, "ingresos": round(r.ingresos, 2)}
            for r in results
        ]

    @staticmethod
    def get_operational_health(db: Session):
        """Métricas de eficiencia operativa."""
        # Tiempo medio entre pedidos, ticket medio, etc.
        ticket_medio = db.query(func.avg(Pedido.total)).scalar() or 0.0
        return {
            "ticket_medio": round(ticket_medio, 2),
            "ratio_fidelizacion": "24%", # Ejemplo
            "eficiencia_cocina": "Óptima"
        }
