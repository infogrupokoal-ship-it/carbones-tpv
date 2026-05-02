import asyncio
import random
import time
from backend.database import SessionLocal
from backend.models import RoboticsTelemetry

async def run_robotics_simulation():
    """
    Simulates real-time robotics telemetry from smart ovens and automated fryers.
    """
    print("🤖 [Robotics] Starting Telemetry Loop...")
    
    while True:
        db = SessionLocal()
        try:
            # Simulate 3 kitchen robots
            for i in range(1, 4):
                robot_id = f"KITCHEN-BOT-0{i}"
                telemetry = RoboticsTelemetry(
                    robot_id=robot_id,
                    status="ACTIVE" if random.random() > 0.1 else "MAINTENANCE",
                    battery_level=random.randint(60, 100),
                    current_task=random.choice(["ASANDO_POLLO", "FRIENDO_PATATAS", "LIMPIEZA", "IDLE"]),
                    last_position="STATION-01",
                    error_logs=None if random.random() > 0.05 else "SENSOR_CALIBRATION_REQUIRED"
                )
                db.add(telemetry)
            
            db.commit()
            # print(f"🤖 [Robotics] {time.strftime('%H:%M:%S')} - Telemetry Batch Committed.")
        except Exception as e:
            print(f"❌ [Robotics] Error: {e}")
        finally:
            db.close()
        
        await asyncio.sleep(60) # Log every minute

if __name__ == "__main__":
    asyncio.run(run_robotics_simulation())
