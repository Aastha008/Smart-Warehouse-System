from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.connection import get_db
from backend.schemas.dashboard import DashboardSummary, RiskTrend, BehaviourStats, LocationStats
from backend.services.dashboard_service import DashboardService
from typing import List

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/summary", response_model=DashboardSummary)
async def get_summary(db: AsyncSession = Depends(get_db)):
    return await DashboardService.get_summary(db)

@router.get("/trends", response_model=List[RiskTrend])
async def get_trends(db: AsyncSession = Depends(get_db)):
    return await DashboardService.get_trends(db)

@router.get("/locations", response_model=List[LocationStats])
async def get_locations(db: AsyncSession = Depends(get_db)):
    return await DashboardService.get_location_stats(db)

@router.get("/behaviours", response_model=List[BehaviourStats])
async def get_behaviours(db: AsyncSession = Depends(get_db)):
    return await DashboardService.get_behaviour_stats(db)
