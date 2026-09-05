from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from backend.database.connection import get_db
from backend.schemas.events import EventResponse, EventCreate, EventStats
from backend.services.event_service import EventService

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("", response_model=List[EventResponse])
async def list_events(
    risk_level: Optional[str] = Query(None, description="Filter by risk level (LOW, MEDIUM, HIGH, CRITICAL)"),
    event_type: Optional[str] = Query(None, description="Filter by behaviour type"),
    location: Optional[str] = Query(None, description="Filter by warehouse location"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    return await EventService.get_events(
        db,
        skip=skip,
        limit=limit,
        risk_level=risk_level,
        event_type=event_type,
        location=location,
        date=date,
        start_date=start_date,
        end_date=end_date,
    )


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate, db: AsyncSession = Depends(get_db)):
    """Create a new warehouse event."""
    return await EventService.create_event(db, event)


@router.get("/high-risk", response_model=List[EventResponse])
async def high_risk_events(limit: int = Query(50, ge=1), db: AsyncSession = Depends(get_db)):
    return await EventService.get_high_risk_events(db, limit=limit)


@router.get("/today", response_model=List[EventResponse])
async def today_events(db: AsyncSession = Depends(get_db)):
    return await EventService.get_today_events(db)


@router.get("/by-location", response_model=List[EventResponse])
async def events_by_location_query(
    location: Optional[str] = Query(None, description="Location to query"),
    db: AsyncSession = Depends(get_db)
):
    if not location:
        return await EventService.get_events(db)
    return await EventService.get_events_by_location(db, location)


@router.get("/by-location/{location}", response_model=List[EventResponse])
async def events_by_location(location: str, db: AsyncSession = Depends(get_db)):
    return await EventService.get_events_by_location(db, location)


@router.get("/statistics", response_model=EventStats)
async def get_statistics(db: AsyncSession = Depends(get_db)):
    stats = await EventService.get_statistics(db)
    return EventStats(**stats)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str, db: AsyncSession = Depends(get_db)):
    event = await EventService.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
    return event


@router.delete("/{event_id}", status_code=status.HTTP_200_OK)
async def delete_event(event_id: str, db: AsyncSession = Depends(get_db)):
    deleted = await EventService.delete_event(db, event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
    return {"message": "Event deleted successfully", "event_id": event_id}
