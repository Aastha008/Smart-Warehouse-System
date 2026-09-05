"""Pydantic schemas for alerts."""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class AlertCreate(BaseModel):
    event_id: Optional[str] = None
    alert_type: str = "visual_audio"
    severity: str = "HIGH"
    message: Optional[str] = None
    location: Optional[str] = None


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_id: Optional[str] = None
    alert_type: str = "visual_audio"
    severity: Optional[str] = "HIGH"
    message: Optional[str] = None
    location: Optional[str] = None
    sent_at: Optional[datetime] = None
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None


class AlertStats(BaseModel):
    total_alerts: int = 0
    unacknowledged_count: int = 0
    critical_count: int = 0
    high_count: int = 0
    acknowledged_count: int = 0

class AlertAcknowledgeResponse(BaseModel):
    message: str = "Acknowledged"
    alert_id: Optional[str] = None
    acknowledged: bool = True
