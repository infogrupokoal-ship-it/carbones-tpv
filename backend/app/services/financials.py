from sqlalchemy.orm import Session
from ..models.product import Producto
from ..models.inventory import RecetaItem, Ingrediente

class FinancialService:
    @staticmethod
    def calculate_product_cost(db: Session, producto_id: str) -> float:
        """Calcula el coste total de producción basado en el escandallo."""
        items = db.query(RecetaItem).filter(RecetaItem.producto_id == producto_id).all()
        total_cost = 0.0
        for item in items:
            ingrediente = db.query(Ingrediente).filter(Ingrediente.id == item.ingrediente_id).first()
            if ingrediente:
                total_cost += item.cantidad_necesaria * ingrediente.coste_por_unidad
        return round(total_cost, 2)

    @staticmethod
    def update_all_product_costs(db: Session):
        """Actualiza el coste estimado de todos los productos en el catálogo."""
        productos = db.query(Producto).all()
        for p in productos:
            p.coste_estimado = FinancialService.calculate_product_cost(db, p.id)
        db.commit()

    @staticmethod
    def get_product_profit_margin(db: Session, producto_id: str) -> dict:
        """Devuelve el análisis de margen de un producto."""
        p = db.query(Producto).filter(Producto.id == producto_id).first()
        if not p:
            return {}
        
        profit = p.precio - p.coste_estimado
        margin_percent = (profit / p.precio * 100) if p.precio > 0 else 0
        
        return {
            "nombre": p.nombre,
            "precio_venta": p.precio,
            "coste_produccion": p.coste_estimado,
            "beneficio_neto": round(profit, 2),
            "margen_porcentaje": round(margin_percent, 2)
        }
