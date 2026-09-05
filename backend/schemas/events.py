from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime


class EventBase(BaseModel):
    """Base event schema with common fields."""
    camera_id: str = "cam_01"
    location: str = "loading_bay_1"
    event_type: str
    risk_level: str
    risk_score: float = 50.0
    confidence: float = 0.5
    object_ids: Optional[Any] = []
    video_path: Optional[str] = None
    video_start: Optional[float] = None
    video_end: Optional[float] = None
    evidence: Optional[Any] = {}
    explanation: Optional[str] = None
    recommendation: Optional[str] = None


class EventCreate(EventBase):
    """Schema for creating a new event."""
    timestamp: Optional[datetime] = None


class EventResponse(BaseModel):
    """Schema for event API responses."""
    model_config = ConfigDict(from_attributes=True)

    event_id: str
    timestamp: datetime
    camera_id: Optional[str] = None
    location: Optional[str] = None
    event_type: Optional[str] = None
    risk_level: Optional[str] = None
    risk_score: Optional[float] = None
    confidence: Optional[float] = None
    object_ids: Optional[Any] = []
    video_path: Optional[str] = None
    video_start: Optional[float] = None
    video_end: Optional[float] = None
    evidence: Optional[Any] = {}
    explanation: Optional[str] = None
    recommendation: Optional[str] = None
    created_at: Optional[datetime] = None


class EventList(BaseModel):
    """Paginated event list."""
    events: List[EventResponse]
    total: int
    limit: int = 100
    offset: int = 0


class EventStats(BaseModel):
    """Comprehensive event statistics."""
    total_events: int = 0
    high_risk: int = 0
    critical: int = 0
    events_today: int = 0
    by_behaviour: Dict[str, int] = {}
    by_location: Dict[str, int] = {}
    by_risk_level: Dict[str, int] = {}
