from fastapi import APIRouter, Depends, HTTPException
from backend.services.aoi_engine import aoi_engine
from typing import List, Dict

router = APIRouter(prefix="/api/aoi", tags=["AOI"])

@router.get("/status")
async def get_aoi_status():
    return {
        "engine": "Singularity AOI",
        "version": aoi_engine.version,
        "status": "OPERATIONAL",
        "health": 99.8
    }

@router.get("/forecast")
async def get_forecast(days: int = 7):
    return aoi_engine.generate_future_forecast(days)

@router.get("/insights")
async def get_insights():
    # In a real app, we'd pass real data here
    return aoi_engine.analyze_business_state([])

@router.get("/actions")
async def get_actions():
    return aoi_engine.get_strategic_actions()
