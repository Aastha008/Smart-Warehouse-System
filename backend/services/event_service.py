"""
AI Warehouse Intelligence - Event Service
CRUD operations and analytics for warehouse events.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, case, and_
from backend.database.models import Event
from backend.schemas.events import EventCreate
import uuid
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, List


def get_current_time():
    return datetime.now(timezone.utc)


class EventService:
    """Service for managing warehouse intelligence events."""

    @staticmethod
    async def get_events(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        risk_level: Optional[str] = None,
        event_type: Optional[str] = None,
        location: Optional[str] = None,
        date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list:
        """Get events with optional filters."""
        query = select(Event)
        if risk_level:
            query = query.where(func.upper(Event.risk_level) == risk_level.upper())
        if event_type:
            query = query.where(Event.event_type == event_type)
        if location:
            query = query.where(Event.location == location)
        if date:
            try:
                dt = datetime.strptime(date, "%Y-%m-%d")
                day_start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timedelta(days=1)
                query = query.where(and_(Event.timestamp >= day_start, Event.timestamp < day_end))
            except Exception:
                pass
        if start_date:
            try:
                dt_start = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.where(Event.timestamp >= dt_start)
            except Exception:
                pass
        if end_date:
            try:
                dt_end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
                query = query.where(Event.timestamp < dt_end)
            except Exception:
                pass

        query = query.order_by(Event.timestamp.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_event(db: AsyncSession, event_id: str):
        """Get a single event by ID."""
        result = await db.execute(
            select(Event).where(Event.event_id == event_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_event(db: AsyncSession, event: EventCreate) -> Event:
        """Create a new event."""
        db_event = Event(
            event_id=str(uuid.uuid4()),
            timestamp=event.timestamp or get_current_time(),
            camera_id=event.camera_id,
            location=event.location,
            event_type=event.event_type,
            risk_level=event.risk_level.upper() if event.risk_level else "MEDIUM",
            risk_score=event.risk_score,
            confidence=event.confidence,
            object_ids=event.object_ids if isinstance(event.object_ids, list) else json.dumps(event.object_ids),
            video_path=event.video_path,
            video_start=event.video_start,
            video_end=event.video_end,
            evidence=event.evidence if isinstance(event.evidence, dict) else json.dumps(event.evidence),
            explanation=event.explanation,
            recommendation=event.recommendation,
        )
        db.add(db_event)
        await db.commit()
        await db.refresh(db_event)
        return db_event

    @staticmethod
    async def get_high_risk_events(db: AsyncSession, limit: int = 50) -> list:
        """Get HIGH and CRITICAL risk events."""
        query = (
            select(Event)
            .where(Event.risk_level.in_(["HIGH", "CRITICAL"]))
            .order_by(Event.timestamp.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_today_events(db: AsyncSession) -> list:
        """Get all events from today."""
        today = get_current_time().replace(hour=0, minute=0, second=0, microsecond=0)
        query = (
            select(Event)
            .where(Event.timestamp >= today)
            .order_by(Event.timestamp.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_events_by_location(db: AsyncSession, location: str) -> list:
        """Get events for a specific location."""
        query = (
            select(Event)
            .where(Event.location == location)
            .order_by(Event.timestamp.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_statistics(db: AsyncSession) -> dict:
        """Get comprehensive event statistics."""
        # Total counts
        total_result = await db.execute(select(func.count(Event.event_id)))
        total = total_result.scalar() or 0

        high_result = await db.execute(
            select(func.count(Event.event_id)).where(Event.risk_level == "HIGH")
        )
        high_risk = high_result.scalar() or 0

        critical_result = await db.execute(
            select(func.count(Event.event_id)).where(Event.risk_level == "CRITICAL")
        )
        critical = critical_result.scalar() or 0

        # Today count
        today = get_current_time().replace(hour=0, minute=0, second=0, microsecond=0)
        today_result = await db.execute(
            select(func.count(Event.event_id)).where(Event.timestamp >= today)
        )
        events_today = today_result.scalar() or 0

        # By behaviour type
        by_behaviour = {}
        behaviour_result = await db.execute(
            select(Event.event_type, func.count(Event.event_id))
            .group_by(Event.event_type)
            .order_by(func.count(Event.event_id).desc())
        )
        for row in behaviour_result.all():
            by_behaviour[row[0]] = row[1]

        # By location
        by_location = {}
        location_result = await db.execute(
            select(Event.location, func.count(Event.event_id))
            .group_by(Event.location)
            .order_by(func.count(Event.event_id).desc())
        )
        for row in location_result.all():
            by_location[row[0]] = row[1]

        # By risk level
        by_risk_level = {}
        risk_result = await db.execute(
            select(Event.risk_level, func.count(Event.event_id))
            .group_by(Event.risk_level)
        )
        for row in risk_result.all():
            by_risk_level[row[0]] = row[1]

        return {
            "total_events": total,
            "high_risk": high_risk,
            "critical": critical,
            "events_today": events_today,
            "by_behaviour": by_behaviour,
            "by_location": by_location,
            "by_risk_level": by_risk_level,
        }

    @staticmethod
    async def get_behaviour_trends(db: AsyncSession, days: int = 7) -> list:
        """Get behaviour event counts per day for the last N days."""
        trends = []
        for i in range(days):
            date = get_current_time().replace(
                hour=0, minute=0, second=0, microsecond=0
            ) - timedelta(days=days - 1 - i)
            next_date = date + timedelta(days=1)

            counts = {}
            for level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
                result = await db.execute(
                    select(func.count(Event.event_id)).where(
                        and_(
                            Event.timestamp >= date,
                            Event.timestamp < next_date,
                            Event.risk_level == level,
                        )
                    )
                )
                counts[level.lower()] = result.scalar() or 0

            trends.append({
                "date": date.strftime("%Y-%m-%d"),
                **counts,
            })

        return trends

    @staticmethod
    async def get_risk_trends(db: AsyncSession, days: int = 7) -> list:
        """Alias for get_behaviour_trends."""
        return await EventService.get_behaviour_trends(db, days)

    @staticmethod
    async def delete_event(db: AsyncSession, event_id: str) -> bool:
        """Delete an event by ID."""
        result = await db.execute(select(Event).where(Event.event_id == event_id))
        event = result.scalar_one_or_none()
        if event:
            await db.delete(event)
            await db.commit()
            return True
        return False
