import asyncio
import httpx
from ..database import SessionLocal
from ..models import Notificacion
from ..utils.logger import logger
from ..config import settings
from datetime import datetime

class NotificationService:
    @staticmethod
    async def send_whatsapp(destino: str, mensaje: str):
        """Envía un mensaje de WhatsApp usando el servicio WAHA."""
        url = f"{settings.WAHA_URL}/api/sendText"
        payload = {
            "chatId": destino,
            "text": mensaje,
            "session": "default"
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10.0)
                return response.status_code == 201
        except Exception as e:
            logger.error(f"Error enviando WhatsApp: {e}")
            return False

    @staticmethod
    def create_notification(db, tipo, destino, mensaje):
        """Helper para crear una notificación persistente."""
        notif = Notificacion(
            tipo=tipo,
            destino=destino,
            mensaje=mensaje,
            estado="PENDIENTE",
            fecha_creacion=datetime.now(datetime.timezone.utc)
        )
        db.add(notif)
        db.commit()
        return notif

    @staticmethod
    async def broadcast_alert(mensaje: str, level: str = "INFO"):
        """Emite una alerta global al sistema (Quantum Broadcast)."""
        logger.warning(f"[BROADCAST_{level}] {mensaje}")
        # En una versión real, esto podría usar WebSockets para alertar a todos los clientes conectados.
        # Por ahora lo dejamos en logs y persistencia si es crítico.
        if level == "CRITICAL":
            db = SessionLocal()
            try:
                NotificationService.create_notification(db, "SYSTEM", "ADMIN", f"CRITICAL: {mensaje}")
            finally:
                db.close()

    @staticmethod
    async def worker_loop():
        """Bucle infinito que procesa la cola de notificaciones en la base de datos."""
        logger.info("[LOG] Iniciando Worker de Notificaciones Enterprise...")
        while True:
            db = SessionLocal()
            try:
                pendientes = db.query(Notificacion).filter(
                    Notificacion.estado == "PENDIENTE",
                    Notificacion.reintentos < 3
                ).limit(5).all()

                for n in pendientes:
                    success = False
                    if n.tipo == "WHATSAPP":
                        success = await NotificationService.send_whatsapp(n.destino, n.mensaje)
                    
                    if success:
                        n.estado = "ENVIADO"
                        n.fecha_envio = datetime.now(datetime.timezone.utc)
                    else:
                        n.reintentos += 1
                        if n.reintentos >= 3:
                            n.estado = "ERROR"
                    
                    db.commit()
            except Exception as e:
                logger.error(f"Error en NotificationWorker: {e}")
            finally:
                db.close()
            
            await asyncio.sleep(30) # Procesar cada 30 segundos
