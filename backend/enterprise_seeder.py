import random
from backend.database import SessionLocal
from backend.models import (
    GhostBrand, RoboticsTelemetry, ESGMétrics, YieldRule, FinancialSnapshot, Tienda
)

def seed_enterprise_data():
    db = SessionLocal()
    try:
        tienda = db.query(Tienda).first()
        if not tienda:
            print("Error: No se encontró ninguna tienda para el seeding enterprise.")
            return

        # 1. Ghost Brands
        if not db.query(GhostBrand).first():
            brands = [
                {"nombre": "Burger Pollos", "slug": "burger-pollos"},
                {"nombre": "Tacos La Granja", "slug": "tacos-la-granja"},
                {"nombre": "Salad Garden TPV", "slug": "salad-garden"}
            ]
            for b in brands:
                db.add(GhostBrand(nombre=b['nombre'], slug=b['slug'], tienda_id=tienda.id))
            print("Ghost Brands sembradas.")

        # 2. Robotics Telemetry
        if not db.query(RoboticsTelemetry).first():
            for i in range(10):
                db.add(RoboticsTelemetry(
                    device_id=f"FRYER-{random.randint(1,4)}",
                    sensor_type="TEMP_FRYER",
                    value=180.0 + random.uniform(-5, 5),
                    unit="C",
                    status="OK"
                ))
            print("Telemetría robótica sembrada.")

        # 3. Yield Rules
        if not db.query(YieldRule).first():
            rules = [
                {"nombre": "Incremento por Lluvia", "clima": "RAIN", "demanda": "HIGH", "pct": 10.0},
                {"nombre": "Descuento por Calor", "clima": "HEAT", "demanda": "LOW", "pct": -5.0}
            ]
            for r in rules:
                db.add(YieldRule(nombre=r['nombre'], condicion_clima=r['clima'], condicion_demanda=r['demanda'], ajuste_precio_pct=r['pct']))
            print("Reglas de Yield sembradas.")

        # 4. Financial Snapshots
        if not db.query(FinancialSnapshot).first():
            db.add(FinancialSnapshot(
                revenue=450000.0,
                ebitda=95000.0,
                burn_rate=30000.0,
                cac=4.5,
                ltv=18.0,
                runway_months=18
            ))
            print("Snapshot financiero sembrado.")

        # 5. ESG Metrics
        if not db.query(ESGMétrics).first():
            db.add(ESGMétrics(
                tienda_id=tienda.id,
                co2_saved_kg=125.5,
                food_waste_kg=12.2,
                plastic_reduced_kg=45.0,
                energy_kwh=1200.0,
                water_liters=4500.0
            ))
            print("Métricas ESG sembradas.")

        db.commit()
        print("--- SEEDING ENTERPRISE V9.0 COMPLETADO ---")
    except Exception as e:
        db.rollback()
        print(f"Error en seeding enterprise: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_enterprise_data()
