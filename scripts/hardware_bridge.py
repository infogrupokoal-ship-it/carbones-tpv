import time
import requests
import json
from backend.config import settings
from backend.utils.logger import logger

class HardwareBridge:
    """Puente de comunicación entre el servidor y el hardware local."""

    def __init__(self, server_url="http://localhost:8000"):
        self.server_url = server_url
        self.is_running = True

    def listen_for_commands(self):
        """Escucha comandos pendientes del servidor (Pooling)."""
        logger.info("🔌 Hardware Bridge Iniciado: Escuchando comandos...")
        while self.is_running:
            try:
                # En un entorno real, esto usaría WebSockets para menor latencia
                response = requests.get(f"{self.server_url}/api/hardware/pending")
                if response.status_code == 200:
                    commands = response.json()
                    for cmd in commands:
                        self.execute_physical_command(cmd)
            except Exception as e:
                logger.warning(f"⚠️ Error de conexión con el servidor: {e}")
            
            time.sleep(2) # Pooling cada 2 segundos

    def execute_physical_command(self, cmd):
        """Ejecuta la acción física (Impresión / Apertura de Cajón)."""
        action = cmd.get("accion")
        logger.info(f"⚙️ Ejecutando comando físico: {action}")
        
        if action == "abrir_caja":
            # Comando ESC/POS para apertura de cajón
            pass
        elif action == "imprimir_ticket":
            # Lógica de impresión térmica
            pass
        
        # Confirmar ejecución al servidor
        requests.post(f"{self.server_url}/api/hardware/confirm/{cmd['id']}")

if __name__ == "__main__":
    # Esto se ejecutaría en el PC de la caja
    bridge = HardwareBridge()
    bridge.listen_for_commands()
