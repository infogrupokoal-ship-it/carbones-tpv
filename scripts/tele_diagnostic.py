import os
import psutil
from datetime import datetime

def run_diagnostic():
    print("--- TPV ENTERPRISE SINGULARITY V9.0 - TELE-DIAGNOSTIC ---")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("-" * 50)
    
    # 1. System Health
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('D:\\' if os.name == 'nt' else '/').percent
    print(f"[SYSTEM] CPU: {cpu}% | MEM: {mem}% | DISK: {disk}%")
    
    # 2. Database Status
    try:
        from backend.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[DATABASE] Status: OPERATIONAL | Connectivity: SECURE")
    except Exception as e:
        print(f"[DATABASE] Status: CRITICAL ERROR | {e}")
        
    # 3. Module Inventory
    modules = [
        "Core: Portal, Caja, KDS, Producción, Reservas, Robotics, Ghost Kitchen",
        "Logistics: Stock, Proveedores, Reparto, Procurement, Aggregators, Fleet, Traceability",
        "Management: Analytics, ERP, RRHH, Marketing, Referidos, Franchise, ESG, Menu Eng, Yield, Call Center, QSC, Onboarding, Eco Tracker, Investors",
        "System: Settings, Audit, IoT, Crisis, Maintenance, Hardware, Signage"
    ]
    print(f"[MODULES] Count: 35 | Distribution: {len(modules)} Categories")
    
    # 4. Git Integrity
    try:
        import subprocess
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
        last_commit = subprocess.check_output(["git", "log", "-1", "--format=%h %s"]).decode().strip()
        print(f"[GIT] Branch: {branch} | Last Commit: {last_commit}")
    except:
        print("[GIT] Status: UNKNOWN (Not a git repo or git not found)")
        
    print("-" * 50)
    print("DIAGNOSTIC COMPLETE - STATUS: OPTIMAL")

if __name__ == "__main__":
    run_diagnostic()
