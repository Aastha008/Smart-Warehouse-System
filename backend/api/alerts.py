from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from backend.database.connection import get_db
from backend.schemas.alerts import AlertResponse, AlertStats, AlertCreate, AlertAcknowledgeResponse
from backend.services.alert_service import AlertService

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=List[AlertResponse])
@router.get("/recent", response_model=List[AlertResponse])
async def get_recent_alerts(
    limit: int = Query(50, ge=1, le=500),
    acknowledged: Optional[bool] = Query(None),
    severity: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get recent warehouse alerts."""
    return await AlertService.get_recent_alerts(
        db, limit=limit, acknowledged=acknowledged, severity=severity
    )


@router.get("/stats", response_model=AlertStats)
async def get_alert_stats(db: AsyncSession = Depends(get_db)):
    """Get aggregated alert metrics."""
    stats = await AlertService.get_alert_stats(db)
    return AlertStats(**stats)


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(alert_data: AlertCreate, db: AsyncSession = Depends(get_db)):
    """Manually create an alert."""
    return await AlertService.create_alert(
        db,
        event_id=alert_data.event_id,
        alert_type=alert_data.alert_type,
        severity=alert_data.severity,
        message=alert_data.message,
        location=alert_data.location,
    )


@router.post("/acknowledge/{alert_id}", response_model=AlertAcknowledgeResponse)
@router.post("/{alert_id}/acknowledge", response_model=AlertAcknowledgeResponse)
async def acknowledge_alert(
    alert_id: str,
    user: Optional[str] = Query(None, description="Supervisor ID or name"),
    db: AsyncSession = Depends(get_db)
):
    """Acknowledge an active alert."""
    alert = await AlertService.acknowledge_alert(db, alert_id, acknowledged_by=user)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    return AlertAcknowledgeResponse(message="Acknowledged", alert_id=alert.id, acknowledged=True)


@router.post("/acknowledge-all")
async def acknowledge_all(
    user: Optional[str] = Query(None, description="Supervisor ID or name"),
    db: AsyncSession = Depends(get_db)
):
    """Acknowledge all unacknowledged alerts."""
    count = await AlertService.acknowledge_all_alerts(db, acknowledged_by=user)
    return {"message": f"Successfully acknowledged {count} alerts", "count": count, "acknowledged": True}

