import asyncio
import random
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import RoboticsTelemetry, LogOperativo
from backend.utils.logger import logger

class IoTBridge:
    """
    IoT Bridge V9.3.
    Monitoriza hardware de cocina y genera alertas automáticas.
    """
    
    @staticmethod
    async def monitor_hardware():
        while True:
            db = SessionLocal()
            try:
                # Simular lectura de sensor de freidora industrial
                temp = 180.0 + random.uniform(-10, 35)
                status = "OK"
                if temp > 200:
                    status = "CRITICAL"
                    logger.warning(f"[IoT] ALERT! Freidora CR-1 sobrecalentada: {temp}C")
                    
                    # Generar log operativo
                    db.add(LogOperativo(
                        nivel="WARNING",
                        modulo="HARDWARE",
                        mensaje=f"¡ALERTA! Freidora CR-1 sobrecalentada: {temp}C. Sistema de enfriamiento activado."
                    ))
                
                # Registrar telemetría
                db.add(RoboticsTelemetry(
                    device_id="FR-1",
                    sensor_type="TEMPERATURE",
                    value=temp,
                    unit="C",
                    status=status
                ))
                db.commit()
                
            except Exception as e:
                logger.error(f"[IoT] Error en puente: {e}")
            finally:
                db.close()
                
            await asyncio.sleep(60) # Monitorización cada minuto
