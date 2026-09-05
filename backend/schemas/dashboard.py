"""Pydantic schemas for dashboard endpoints."""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class DashboardSummary(BaseModel):
    """Dashboard summary metrics."""
    total_events_today: int = 0
    high_risk_events_today: int = 0
    critical_events_today: int = 0
    active_alerts: int = 0
    total_events: int = 0
    high_risk_count: int = 0
    critical_count: int = 0


class RiskTrend(BaseModel):
    """Risk trend data point."""
    date: str
    risk_level: str
    count: int = 0


class BehaviourStats(BaseModel):
    """Behaviour type statistics."""
    behaviour: str
    count: int = 0


class LocationStats(BaseModel):
    """Location-based statistics."""
    location: str
    events_count: int = 0
    high_risk_count: int = 0
