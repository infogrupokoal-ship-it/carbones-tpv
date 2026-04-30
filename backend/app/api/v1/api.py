from fastapi import APIRouter
from .endpoints import auth, orders, admin

api_router = APIRouter()

# Registro modular de dominios Enterprise
api_router.include_router(auth.router, prefix="/auth", tags=["Seguridad y Acceso"])
api_router.include_router(orders.router, prefix="/orders", tags=["Ventas y Transacciones"])
api_router.include_router(admin.router, prefix="/admin", tags=["Gobernanza y Sistema"])

@api_router.get("/status", tags=["Salud"])
def get_api_status():
    return {
        "api_v1": "active",
        "protocol": "enterprise-industrial",
        "auth_engine": "bcrypt-jwt"
    }
