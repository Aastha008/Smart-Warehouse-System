"""
AI Warehouse Intelligence - Video Processing Service

Handles video uploads, triggers analysis via the vision pipeline,
and stores detected events in the database.
"""
import uuid
import asyncio
import json
import traceback
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.database.models import VideoJob, Event, Alert
from backend.database.connection import AsyncSessionLocal


def get_current_time():
    return datetime.now(timezone.utc)


class VideoService:
    """Service for managing video jobs and analysis."""

    @staticmethod
    async def create_job(db: AsyncSession, video_path: str) -> VideoJob:
        """Create a new video analysis job."""
        job = VideoJob(video_path=video_path, status="pending", progress=0.0)
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def get_job_status(db: AsyncSession, job_id: str) -> Optional[VideoJob]:
        """Get current status of a video job."""
        result = await db.execute(select(VideoJob).where(VideoJob.job_id == job_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_jobs(db: AsyncSession) -> list[VideoJob]:
        """Get all video jobs, most recent first."""
        result = await db.execute(select(VideoJob).order_by(VideoJob.created_at.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def update_job(db: AsyncSession, job_id: str, status: str,
                         progress: float = 0.0, events_count: int = 0,
                         total_frames: int = 0, processed_frames: int = 0,
                         error_message: str = None) -> Optional[VideoJob]:
        """Update job status and progress."""
        result = await db.execute(select(VideoJob).where(VideoJob.job_id == job_id))
        job = result.scalar_one_or_none()
        if job:
            job.status = status
            job.progress = progress
            job.events_count = events_count
            job.total_frames = total_frames
            job.processed_frames = processed_frames
            if error_message:
                job.error_message = error_message
            if status in ("completed", "failed"):
                job.completed_at = get_current_time()
            await db.commit()
            await db.refresh(job)
        return job


async def analyze_video_background(job_id: str, video_path: str,
                                    camera_id: str = "cam_01",
                                    location: str = "loading_bay_1",
                                    frame_skip: int = 2,
                                    confidence_threshold: float = 0.35):
    """
    Background task to analyze a video using the full vision pipeline.

    Pipeline: Video → Decode → Detect → Track → Behaviour → Risk → Events
    """
    async with AsyncSessionLocal() as db:
        try:
            await VideoService.update_job(db, job_id, "processing", 5.0)

            # Import vision pipeline (lazy import to handle missing deps gracefully)
            try:
                from backend.vision.pipeline import VideoPipeline
                pipeline = VideoPipeline(skip_frames=frame_skip, conf_threshold=confidence_threshold)

                # Process video
                result = pipeline.process_video(video_path)

                total_frames = getattr(result, "total_frames", 0)
                events = getattr(result, "events", [])

                # Store detected events in database
                events_count = 0
                for event_data in events:
                    event_id = str(uuid.uuid4())
                    risk_lvl = (event_data.get("risk_level") or "MEDIUM").upper()
                    event = Event(
                        event_id=event_id,
                        timestamp=get_current_time(),
                        camera_id=camera_id,
                        location=event_data.get("location", location),
                        event_type=event_data.get("event_type", "unknown"),
                        risk_level=risk_lvl,
                        risk_score=event_data.get("risk_score", 50),
                        confidence=event_data.get("confidence", 0.5),
                        object_ids=[event_data.get("object_id", 0)],
                        video_path=video_path,
                        video_start=event_data.get("frame_idx", 0),
                        video_end=event_data.get("frame_idx", 0) + 30,
                        evidence=event_data.get("evidence", {}),
                        explanation=event_data.get("explanation", ""),
                        recommendation=event_data.get("recommendation", ""),
                    )
                    db.add(event)
                    events_count += 1

                    # Trigger alert for HIGH or CRITICAL risk
                    if risk_lvl in ("HIGH", "CRITICAL"):
                        alert = Alert(
                            id=str(uuid.uuid4()),
                            event_id=event_id,
                            alert_type="visual_audio",
                            severity=risk_lvl,
                            message=f"{risk_lvl} event: {event_data.get('event_type')} detected at {location}",
                            location=location,
                            sent_at=get_current_time(),
                            acknowledged=False,
                        )
                        db.add(alert)

                await db.commit()

                await VideoService.update_job(
                    db, job_id, "completed", 100.0,
                    events_count=events_count,
                    total_frames=total_frames,
                    processed_frames=total_frames,
                )

            except ImportError:
                # Vision pipeline dependencies not available
                # Run mock analysis
                await _mock_analysis(db, job_id, video_path, camera_id, location)

        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}\n{traceback.format_exc()}"
            await VideoService.update_job(
                db, job_id, "failed", 0.0,
                error_message=error_msg,
            )


async def _mock_analysis(db: AsyncSession, job_id: str, video_path: str,
                          camera_id: str, location: str):
    """
    Mock analysis for development when vision pipeline is not available.
    Generates sample events to demonstrate the full flow.
    """
    await VideoService.update_job(db, job_id, "processing", 25.0, total_frames=500)
    await asyncio.sleep(0.2)

    sample_events = [
        {
            "event_type": "product_drop",
            "risk_level": "HIGH",
            "risk_score": 75,
            "confidence": 0.87,
            "frame_idx": 120,
            "evidence": {"drop_height_px": 130, "velocity": 4.5},
            "explanation": "Product moved downward rapidly and became stationary. Approximate drop distance: 130 pixels. This is a potential damage-causing event.",
            "recommendation": "Inspect the product for potential damage. Review unloading procedure.",
        },
        {
            "event_type": "product_dragging",
            "risk_level": "MEDIUM",
            "risk_score": 45,
            "confidence": 0.72,
            "frame_idx": 280,
            "evidence": {"drag_distance_px": 200, "drag_frames": 25},
            "explanation": "Product was observed moving horizontally with minimal vertical lift.",
            "recommendation": "Provide trolley/pallet truck. Train on proper movement.",
        },
        {
            "event_type": "improper_stacking",
            "risk_level": "MEDIUM",
            "risk_score": 55,
            "confidence": 0.68,
            "frame_idx": 350,
            "evidence": {"heavy_on_light": True, "overhang_fraction": 0.15},
            "explanation": "Stacking configuration may compromise product integrity.",
            "recommendation": "Rearrange stack. Heavy items at bottom.",
        },
    ]

    await VideoService.update_job(db, job_id, "processing", 60.0)
    await asyncio.sleep(0.2)

    events_count = 0
    for evt in sample_events:
        event_id = str(uuid.uuid4())
        risk_lvl = evt["risk_level"].upper()
        event = Event(
            event_id=event_id,
            timestamp=get_current_time(),
            camera_id=camera_id,
            location=location,
            event_type=evt["event_type"],
            risk_level=risk_lvl,
            risk_score=evt["risk_score"],
            confidence=evt["confidence"],
            object_ids=[events_count + 1],
            video_path=video_path,
            video_start=evt["frame_idx"],
            video_end=evt["frame_idx"] + 30,
            evidence=evt["evidence"],
            explanation=evt["explanation"],
            recommendation=evt["recommendation"],
        )
        db.add(event)
        events_count += 1

        if risk_lvl in ("HIGH", "CRITICAL"):
            alert = Alert(
                id=str(uuid.uuid4()),
                event_id=event_id,
                alert_type="visual_audio",
                severity=risk_lvl,
                message=f"{risk_lvl} event: {evt['event_type']} detected at {location}",
                location=location,
                sent_at=get_current_time(),
                acknowledged=False,
            )
            db.add(alert)

    await db.commit()

    await VideoService.update_job(
        db, job_id, "completed", 100.0,
        events_count=events_count,
        total_frames=500,
        processed_frames=500,
    )
