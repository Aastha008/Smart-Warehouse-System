"""Pydantic schemas for video processing."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VideoUploadResponse(BaseModel):
    """Response after video upload."""
    job_id: str
    filename: str = ""
    status: str = "uploaded"
    message: str = "Video uploaded successfully"
    scenario: Optional[dict] = None


class VideoJobStatus(BaseModel):
    """Video analysis job status."""
    job_id: str
    status: str = "pending"
    progress: float = 0.0
    total_frames: int = 0
    processed_frames: int = 0
    events_count: int = 0
    error_message: Optional[str] = None


class AnalysisRequest(BaseModel):
    """Request to start video analysis."""
    job_id: str
    camera_id: str = "cam_01"
    location: str = "loading_bay_1"
    frame_skip: int = 2
    confidence_threshold: float = 0.35
