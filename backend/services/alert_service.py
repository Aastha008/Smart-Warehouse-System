from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_
from backend.database.models import Alert
from datetime import datetime, timezone
from typing import Optional, List
import uuid


def get_current_time():
    return datetime.now(timezone.utc)


class AlertService:
    @staticmethod
    async def create_alert(
        db: AsyncSession,
        event_id: Optional[str] = None,
        alert_type: str = "visual_audio",
        severity: str = "HIGH",
        message: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Alert:
        alert = Alert(
            id=str(uuid.uuid4()),
            event_id=event_id,
            alert_type=alert_type,
            severity=severity.upper() if severity else "HIGH",
            message=message,
            location=location,
            sent_at=get_current_time(),
            acknowledged=False,
        )
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        return alert

    @staticmethod
    async def get_recent_alerts(
        db: AsyncSession,
        limit: int = 50,
        acknowledged: Optional[bool] = None,
        severity: Optional[str] = None,
    ) -> List[Alert]:
        query = select(Alert)
        if acknowledged is not None:
            query = query.where(Alert.acknowledged == acknowledged)
        if severity:
            query = query.where(func.upper(Alert.severity) == severity.upper())
        query = query.order_by(Alert.sent_at.desc()).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_alert_by_id(db: AsyncSession, alert_id: str) -> Optional[Alert]:
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def acknowledge_alert(
        db: AsyncSession,
        alert_id: str,
        acknowledged_by: Optional[str] = None,
    ) -> Optional[Alert]:
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()
        if alert:
            alert.acknowledged = True
            alert.acknowledged_at = get_current_time()
            if acknowledged_by:
                alert.acknowledged_by = acknowledged_by
            await db.commit()
            await db.refresh(alert)
        return alert

    @staticmethod
    async def acknowledge_all_alerts(
        db: AsyncSession,
        acknowledged_by: Optional[str] = None,
    ) -> int:
        from sqlalchemy import update
        now = get_current_time()
        stmt = (
            update(Alert)
            .where(Alert.acknowledged == False)
            .values(
                acknowledged=True,
                acknowledged_at=now,
                acknowledged_by=acknowledged_by or "Shift Lead",
            )
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount or 0

    @staticmethod
    async def get_alert_stats(db: AsyncSession) -> dict:
        total_res = await db.execute(select(func.count(Alert.id)))
        total = total_res.scalar() or 0

        unack_res = await db.execute(
            select(func.count(Alert.id)).where(Alert.acknowledged == False)
        )
        unack = unack_res.scalar() or 0

        crit_res = await db.execute(
            select(func.count(Alert.id)).where(
                and_(Alert.severity == "CRITICAL", Alert.acknowledged == False)
            )
        )
        critical = crit_res.scalar() or 0

        high_res = await db.execute(
            select(func.count(Alert.id)).where(
                and_(Alert.severity == "HIGH", Alert.acknowledged == False)
            )
        )
        high = high_res.scalar() or 0

        ack_res = await db.execute(
            select(func.count(Alert.id)).where(Alert.acknowledged == True)
        )
        ack = ack_res.scalar() or 0

        return {
            "total_alerts": total,
            "unacknowledged_count": unack,
            "critical_count": critical,
            "high_count": high,
            "acknowledged_count": ack,
        }
