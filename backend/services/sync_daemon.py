import asyncio
import logging

logger = logging.getLogger(__name__)

async def run():
    """
    Sync Daemon (Background Worker)
    Mantiene sincronizados los estados entre Render, Base de datos local y APIs externas.
    """
    from backend.services.ai_bi_agent import BusinessAIAgent
    from backend.database import SessionLocal
    
    agent = BusinessAIAgent()
    
    while True:
        try:
            # Ejecutar análisis estratégico
            db = SessionLocal()
            try:
                await agent.analyze_and_notify(db)
            finally:
                db.close()
                
            await asyncio.sleep(3600)  # Ejecutar cada hora
        except asyncio.CancelledError:
            logger.info("Sync Daemon detenido.")
            break
        except Exception as e:
            logger.error(f"Error en Sync Daemon: {e}")
            await asyncio.sleep(60) # Esperar antes de reintentar
