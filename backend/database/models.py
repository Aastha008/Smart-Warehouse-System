from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, ForeignKey
from datetime import datetime, timezone
from backend.database.connection import Base
import uuid


def utc_now():
    return datetime.now(timezone.utc)


class Event(Base):
    __tablename__ = 'events'
    event_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=utc_now)
    camera_id = Column(String, default="cam_01")
    location = Column(String, default="loading_bay_1")
    event_type = Column(String, nullable=False)
    risk_level = Column(String, default="MEDIUM")
    risk_score = Column(Float, default=50.0)
    confidence = Column(Float, default=0.5)
    object_ids = Column(JSON, default=list)
    video_path = Column(String, nullable=True)
    video_start = Column(Float, nullable=True)
    video_end = Column(Float, nullable=True)
    evidence = Column(JSON, default=dict)
    explanation = Column(String, nullable=True)
    recommendation = Column(String, nullable=True)
    created_at = Column(DateTime, default=utc_now)


class VideoJob(Base):
    __tablename__ = 'video_jobs'
    job_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    video_path = Column(String, nullable=False)
    status = Column(String, default='pending')
    progress = Column(Float, default=0.0)
    total_frames = Column(Integer, default=0)
    processed_frames = Column(Integer, default=0)
    events_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)


class Alert(Base):
    __tablename__ = 'alert_logs'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String, ForeignKey('events.event_id', ondelete='SET NULL'), nullable=True)
    alert_type = Column(String, default="visual_audio")
    severity = Column(String, default="HIGH")
    message = Column(String, nullable=True)
    location = Column(String, nullable=True)
    sent_at = Column(DateTime, default=utc_now)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String, nullable=True)


# Backwards compatibility alias
AlertLog = Alert


class Camera(Base):
    __tablename__ = 'cameras'
    camera_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    rtsp_url = Column(String, nullable=True)
    status = Column(String, default="active")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)


class Metric(Base):
    __tablename__ = 'metrics'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=utc_now)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    location = Column(String, nullable=True)
    metadata_json = Column(JSON, default=dict)
