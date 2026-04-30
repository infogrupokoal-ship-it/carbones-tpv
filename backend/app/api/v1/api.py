from fastapi import APIRouter
from .endpoints import auth, orders, inventory

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])

# Endpoint de Analíticas consolidado
@api_router.get("/analytics/kpis", tags=["analytics"])
def get_kpis():
    # Mock data pro para el dashboard hasta conectar DB real
    return {
        "total_ventas": 1240.50,
        "numero_pedidos": 84,
        "margen_promedio": 68.4,
        "coste_materia_prima": 392.10,
        "tendencia": "up"
    }
