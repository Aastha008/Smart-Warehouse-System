from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, and_
from backend.services.event_service import EventService
from backend.database.models import Event, Alert
from datetime import datetime, timedelta, timezone


def get_current_time():
    return datetime.now(timezone.utc)


class DashboardService:
    """Service for dashboard data aggregation."""

    @staticmethod
    async def get_summary(db: AsyncSession) -> dict:
        """Get dashboard summary with key metrics."""
        stats = await EventService.get_statistics(db)

        # Count unacknowledged alerts
        try:
            alerts_result = await db.execute(
                select(func.count(Alert.id)).where(Alert.acknowledged == False)
            )
            active_alerts = alerts_result.scalar() or 0
        except Exception:
            active_alerts = 0

        return {
            "total_events_today": stats.get("events_today", 0),
            "high_risk_events_today": stats.get("high_risk", 0),
            "critical_events_today": stats.get("critical", 0),
            "active_alerts": active_alerts,
            "total_events": stats.get("total_events", 0),
            "high_risk_count": stats.get("high_risk", 0),
            "critical_count": stats.get("critical", 0),
        }

    @staticmethod
    async def get_trends(db: AsyncSession, days: int = 7) -> list:
        """Get risk trends over the last N days."""
        trends = []
        now = get_current_time()
        for i in range(days):
            date = now.replace(
                hour=0, minute=0, second=0, microsecond=0
            ) - timedelta(days=days - 1 - i)
            next_date = date + timedelta(days=1)

            for level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
                result = await db.execute(
                    select(func.count(Event.event_id)).where(
                        and_(
                            Event.timestamp >= date,
                            Event.timestamp < next_date,
                            func.upper(Event.risk_level) == level,
                        )
                    )
                )
                trends.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "risk_level": level,
                    "count": result.scalar() or 0,
                })

        return trends

    @staticmethod
    async def get_location_stats(db: AsyncSession) -> list:
        """Get event counts by location."""
        result = await db.execute(
            select(
                Event.location,
                func.count(Event.event_id).label("events_count"),
            )
            .group_by(Event.location)
            .order_by(func.count(Event.event_id).desc())
        )
        rows = result.all()

        stats = []
        for row in rows:
            location = row[0]
            total = row[1]

            # Count high risk for this location
            hr_result = await db.execute(
                select(func.count(Event.event_id)).where(
                    and_(
                        Event.location == location,
                        Event.risk_level.in_(["HIGH", "CRITICAL"]),
                    )
                )
            )
            high_risk = hr_result.scalar() or 0

            stats.append({
                "location": location or "Unknown",
                "events_count": total,
                "high_risk_count": high_risk,
            })

        # If no data, return default zones
        if not stats:
            stats = [
                {"location": "Loading Bay 1", "events_count": 0, "high_risk_count": 0},
                {"location": "Loading Bay 2", "events_count": 0, "high_risk_count": 0},
                {"location": "Loading Bay 3", "events_count": 0, "high_risk_count": 0},
            ]

        return stats

    @staticmethod
    async def get_behaviour_stats(db: AsyncSession) -> list:
        """Get event counts by behaviour type."""
        result = await db.execute(
            select(
                Event.event_type,
                func.count(Event.event_id).label("count"),
            )
            .group_by(Event.event_type)
            .order_by(func.count(Event.event_id).desc())
        )
        rows = result.all()

        stats = []
        for row in rows:
            stats.append({
                "behaviour": (row[0] or "unknown").replace("_", " ").title(),
                "count": row[1],
            })

        # If no data, return defaults
        if not stats:
            stats = [
                {"behaviour": "Product Drop", "count": 0},
                {"behaviour": "Product Dragging", "count": 0},
                {"behaviour": "Improper Stacking", "count": 0},
            ]

        return stats
