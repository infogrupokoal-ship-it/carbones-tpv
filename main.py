import uvicorn
import os
import logging
from backend.main import app

# Configuración básica de arranque para producción (Render)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logging.info(f"Iniciando TPV Enterprise en puerto {port}...")
    
    # En producción, delegamos todo al backend modular
    uvicorn.run(app, host="0.0.0.0", port=port)
