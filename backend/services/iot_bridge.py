import random
import asyncio
from datetime import datetime
from typing import Dict, List

class IoTBridge:
    """
    Simulated IoT Bridge for Hardware Telemetry.
    Connects with thermal printers, scales, and smart kitchen equipment.
    """
    
    def __init__(self):
        self.devices = [
            {"id": "PRN-01", "name": "Impresora Térmica (Cocina)", "status": "online", "paper": 85},
            {"id": "SCL-01", "name": "Báscula de Pesaje", "status": "online", "load": 0},
            {"id": "FRG-01", "name": "Cámara Frigorífica 1", "status": "online", "temp": 3.4},
            {"id": "OVEN-01", "name": "Horno de Asado", "status": "online", "temp": 185}
        ]

    def get_device_status(self) -> List[Dict]:
        # Simulate slight variations
        for d in self.devices:
            if d['id'] == "FRG-01":
                d['temp'] = round(3.4 + random.uniform(-0.5, 0.5), 1)
            if d['id'] == "PRN-01":
                d['paper'] -= random.randint(0, 1)
                if d['paper'] < 5: d['paper'] = 100 # Simulated reload
        return self.devices

    async def run_monitoring_loop(self):
        """Background loop to check for hardware failures."""
        while True:
            # Randomly trigger a hardware warning
            if random.random() < 0.05:
                device = random.choice(self.devices)
                # In a real app, this would trigger a notification
                print(f"[IoT Bridge] Warning: Device {device['id']} reporting anomaly.")
            await asyncio.sleep(60)

# Global Instance
iot_bridge = IoTBridge()
