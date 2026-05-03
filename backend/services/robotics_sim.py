import asyncio
import random
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
                    device_id=robot_id,
                    sensor_type=random.choice(["TEMP_FRYER", "OIL_QUALITY", "DISPENSE_COUNT"]),
                    value=random.uniform(150.0, 190.0) if "TEMP" in robot_id else random.random(),
                    unit="°C" if "TEMP" in robot_id else "%",
                    status="OK" if random.random() > 0.1 else "WARNING"
                )
                db.add(telemetry)
            
            db.commit()
            # print(f"🤖 [Robotics] {time.strftime('%H:%M:%S')} - Telemetry Batch Committed.")
        except Exception as e:
            print(f"❌ [Robotics] Error: {e}")
        finally:
            db.close()
        
        await asyncio.sleep(60) # Log every minute

def start_robotics_sim():
    """Wrapper to run the async simulation in a thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_robotics_simulation())

if __name__ == "__main__":
    asyncio.run(run_robotics_simulation())
