from fastapi.openapi.utils import get_openapi

def custom_openapi(app):
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Carbones y Pollos - API Directiva Enterprise",
        version="2.6.0",
        description="""
        ## 🚀 Interfaz de Control de Operaciones
        Esta API permite la integración total de terminales TPV, KDS de cocina, y el motor de inteligencia operacional Koal-AI.
        
        ### 🔒 Seguridad
        Todos los endpoints están protegidos por middleware de auditoría y, opcionalmente, JWT.
        """,
        routes=app.routes,
    )
    
    # Personalización estética de Swagger (Añadir logo/colores)
    openapi_schema["info"]["x-logo"] = {
        "url": "https://grupokoal.com/assets/tpv_logo.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema
