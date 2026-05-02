from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.aoi_engine import AOIEngine

router = APIRouter(prefix="/api/aoi", tags=["AI Intelligence"])

@router.get("/predictive")
def get_predictive_analysis(db: Session = Depends(get_db)):
    return AOIEngine.predict_sales_next_24h(db)

@router.get("/esg")
def get_esg_report(db: Session = Depends(get_db)):
    return AOIEngine.get_esg_impact_summary(db)

@router.get("/optimization")
def get_menu_optimization(db: Session = Depends(get_db)):
    return AOIEngine.get_menu_optimization_tips(db)
