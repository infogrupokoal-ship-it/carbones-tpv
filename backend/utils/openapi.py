from fastapi import FastAPI
from backend.config import settings

def setup_openapi(app: FastAPI):
    """Configuración profesional de la documentación de la API."""
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="""
        ## Ecosistema Enterprise Carbones y Pollos TPV
        Esta API es el núcleo operativo de la cadena de asadores.
        
        ### Seguridad
        - **OAuth2 / JWT**: Para acceso administrativo y de terminales.
        - **PIN de Acceso**: Para personal de sala y cocina.
        
        ### Módulos Principales
        * **Operaciones**: Gestión de pedidos en tiempo real.
        * **Logística**: Control de stock fraccional y mermas.
        * **BI & IA**: Analítica predictiva y asistente ejecutivo.
        """,
        routes=app.routes,
    )
    
    # Custom tags and descriptions
    openapi_schema["info"]["x-logo"] = {
        "url": "/static/img/logo_enterprise.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema
