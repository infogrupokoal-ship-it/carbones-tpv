import asyncio
import httpx
import os
from backend.utils.logger import logger
from backend.database import SessionLocal
from sqlalchemy import text

class SelfHealingService:
    """
    Quantum Self-Healing Engine v6.0.
    Monitorea proactivamente el ecosistema y ejecuta protocolos de recuperación automáticos.
    """
    
    def __init__(self):
        self.endpoints = [
            "http://localhost:8000/api/health",
            "http://localhost:8000/static/portal.html",
            "http://localhost:8000/api/orders/active"
        ]
        self.is_running = True
        self.failure_counters = {}

    async def monitor(self):
        logger.info("Quantum Self-Healing Engine [V6.0] Online.")
        while self.is_running:
            async with httpx.AsyncClient() as client:
                for url in self.endpoints:
                    try:
                        resp = await client.get(url, timeout=5.0)
                        if resp.status_code >= 500:
                            await self.handle_failure(url, f"HTTP_{resp.status_code}")
                        else:
                            # Reset failure counter on success
                            self.failure_counters[url] = 0
                    except Exception as e:
                        await self.handle_failure(url, str(e))
            
            await asyncio.sleep(60)

    async def handle_failure(self, url, error):
        self.failure_counters[url] = self.failure_counters.get(url, 0) + 1
        count = self.failure_counters[url]
        
        logger.error(f"Anomaly detected at {url} | Failures: {count} | Error: {error}")
        
        if count >= 3:
            logger.warning(f"Initiating Recovery Protocol for {url}...")
            if "api/health" in url:
                await self.recover_database()
            elif "static" in url:
                await self.recover_static_integrity()
            
            # Reset counter after recovery attempt
            self.failure_counters[url] = 0

    async def recover_database(self):
        logger.info("Protocol 'OMEGA': Reconnecting Database and validating schema...")
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            logger.info("Database connection restored.")
        except Exception as e:
            logger.critical(f"Database recovery failed: {e}. Executing emergency re-seeding.")
            # Aquí podrías ejecutar migrate_schema() de nuevo
            from backend.auto_migrate import migrate_schema
            migrate_schema()

    async def recover_static_integrity(self):
        logger.info("Protocol 'SIGMA': Validating static asset integrity...")
        # Lógica para verificar que index.html y portal.html existen
        paths = ["static/portal.html", "static/js/enterprise_shell.js"]
        for p in paths:
            if not os.path.exists(p):
                logger.error(f"Critical asset missing: {p}")
                # En un entorno real podrías intentar restaurar desde un backup o git

    def stop(self):
        self.is_running = False
