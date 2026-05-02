from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..services.autonomous_dispatch import dispatcher
from ..services.yield_pricing import yield_engine
from ..services.iot_bridge import iot_bridge
from typing import List, Dict

router = APIRouter(prefix="/api/enterprise", tags=["Enterprise Singularity"])

@router.get("/global-status")
def get_global_status(db: Session = Depends(get_db)):
    """Aggregated status of the entire enterprise singularity."""
    return {
        "nodes": {
            "stores": db.query(models.Tienda).count(),
            "active_users": db.query(models.Usuario).filter(models.Usuario.is_active == True).count(),
            "total_orders_today": db.query(models.Pedido).count(),
            "iot_devices": len(iot_bridge.get_device_status()),
        },
        "logistics": dispatcher.get_logistics_telemetry(),
        "market": yield_engine.get_market_insights(),
        "performance": {
            "avg_prep_time": "14m",
            "delivery_efficiency": f"{dispatcher.optimization_score}%",
            "system_uptime": "99.99%"
        },
        "ai_status": "Active / Optimal"
    }

@router.get("/franchise-data")
def get_franchise_data(db: Session = Depends(get_db)):
    """Financial and operational data for franchises."""
    return db.query(models.FranchiseContract).all()

@router.get("/esg-monitor")
def get_esg_data(db: Session = Depends(get_db)):
    """Environmental, Social and Governance metrics."""
    return db.query(models.ESGMétrics).all()
