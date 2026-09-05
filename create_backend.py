import os
import json

base = r"C:\Users\hp\.gemini\antigravity\scratch\ai-warehouse-intelligence\backend"

files = {}

files[r"utils\config.py"] = """
import yaml
from pathlib import Path
import os
from functools import lru_cache

class Config:
    def __init__(self):
        self.config = {}
        # Load default or create dummy
        pass

@lru_cache()
def get_config():
    return Config()
"""

files[r"utils\logger.py"] = """
import sys
from loguru import logger

logger.remove()
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

def get_logger(name):
    return logger.bind(name=name)
"""

files[r"database\connection.py"] = """
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./warehouse.db")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
"""

files[r"database\models.py"] = """
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, ForeignKey
from datetime import datetime
from backend.database.connection import Base
import uuid

class Event(Base):
    __tablename__ = 'events'
    event_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow)
    camera_id = Column(String)
    location = Column(String)
    event_type = Column(String)
    risk_level = Column(String)
    risk_score = Column(Float)
    confidence = Column(Float)
    object_ids = Column(JSON)
    video_path = Column(String)
    video_start = Column(Float)
    video_end = Column(Float)
    evidence = Column(JSON)
    explanation = Column(String)
    recommendation = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class VideoJob(Base):
    __tablename__ = 'video_jobs'
    job_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    video_path = Column(String)
    status = Column(String, default='pending')
    progress = Column(Float, default=0.0)
    total_frames = Column(Integer, default=0)
    processed_frames = Column(Integer, default=0)
    events_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)

class AlertLog(Base):
    __tablename__ = 'alert_logs'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String, ForeignKey('events.event_id'))
    alert_type = Column(String)
    sent_at = Column(DateTime, default=datetime.utcnow)
    acknowledged = Column(Boolean, default=False)
"""

files[r"schemas\events.py"] = """
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class EventBase(BaseModel):
    camera_id: str
    location: str
    event_type: str
    risk_level: str
    risk_score: float
    confidence: float
    object_ids: Optional[List[str]] = []
    video_path: Optional[str] = None
    video_start: Optional[float] = None
    video_end: Optional[float] = None
    evidence: Optional[Dict[str, Any]] = {}
    explanation: Optional[str] = None
    recommendation: Optional[str] = None

class EventCreate(EventBase):
    timestamp: Optional[datetime] = None

class EventResponse(EventBase):
    event_id: str
    timestamp: datetime
    created_at: datetime
    class Config:
        from_attributes = True

class EventList(BaseModel):
    events: List[EventResponse]
    total: int

class EventStats(BaseModel):
    total_events: int
    high_risk: int
    critical: int
"""

files[r"schemas\video.py"] = """
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VideoUploadResponse(BaseModel):
    job_id: str
    status: str
    message: str

class VideoJobStatus(BaseModel):
    job_id: str
    status: str
    progress: float
    events_count: int
    error_message: Optional[str] = None

class AnalysisRequest(BaseModel):
    video_path: str
    camera_id: str
    location: str
"""

files[r"schemas\dashboard.py"] = """
from pydantic import BaseModel
from typing import List, Dict, Any

class DashboardSummary(BaseModel):
    total_events_today: int
    high_risk_events_today: int
    critical_events_today: int
    active_alerts: int

class RiskTrend(BaseModel):
    date: str
    risk_level: str
    count: int

class BehaviourStats(BaseModel):
    behaviour: str
    count: int

class LocationStats(BaseModel):
    location: str
    events_count: int
    high_risk_count: int
"""

files[r"schemas\assistant.py"] = """
from pydantic import BaseModel

class AssistantQuery(BaseModel):
    query: str
    context: dict = {}

class AssistantResponse(BaseModel):
    response: str
    data_used: dict = {}
"""

files[r"services\event_service.py"] = """
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from backend.database.models import Event
from backend.schemas.events import EventCreate
import uuid
from datetime import datetime, timedelta

class EventService:
    @staticmethod
    async def get_events(db: AsyncSession, skip: int = 0, limit: int = 100, risk_level: str = None):
        query = select(Event)
        if risk_level:
            query = query.where(Event.risk_level == risk_level)
        query = query.order_by(Event.timestamp.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_event(db: AsyncSession, event_id: str):
        result = await db.execute(select(Event).where(Event.event_id == event_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_event(db: AsyncSession, event: EventCreate):
        db_event = Event(**event.model_dump())
        if not db_event.timestamp:
            db_event.timestamp = datetime.utcnow()
        db.add(db_event)
        await db.commit()
        await db.refresh(db_event)
        return db_event

    @staticmethod
    async def get_high_risk_events(db: AsyncSession):
        return await EventService.get_events(db, risk_level="HIGH")

    @staticmethod
    async def get_today_events(db: AsyncSession):
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        query = select(Event).where(Event.timestamp >= today)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_events_by_location(db: AsyncSession, location: str):
        query = select(Event).where(Event.location == location)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_statistics(db: AsyncSession):
        total = await db.execute(select(func.count(Event.event_id)))
        high = await db.execute(select(func.count(Event.event_id)).where(Event.risk_level == 'HIGH'))
        critical = await db.execute(select(func.count(Event.event_id)).where(Event.risk_level == 'CRITICAL'))
        
        return {
            "total_events": total.scalar() or 0,
            "high_risk": high.scalar() or 0,
            "critical": critical.scalar() or 0
        }
"""

files[r"services\video_service.py"] = """
import uuid
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.database.models import VideoJob
from datetime import datetime
from backend.database.connection import AsyncSessionLocal

class VideoService:
    @staticmethod
    async def create_job(db: AsyncSession, video_path: str):
        job = VideoJob(video_path=video_path)
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def get_job_status(db: AsyncSession, job_id: str):
        result = await db.execute(select(VideoJob).where(VideoJob.job_id == job_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_jobs(db: AsyncSession):
        result = await db.execute(select(VideoJob).order_by(VideoJob.created_at.desc()))
        return result.scalars().all()

    @staticmethod
    async def update_job(db: AsyncSession, job_id: str, status: str, progress: float = 0.0):
        result = await db.execute(select(VideoJob).where(VideoJob.job_id == job_id))
        job = result.scalar_one_or_none()
        if job:
            job.status = status
            job.progress = progress
            if status in ['completed', 'failed']:
                job.completed_at = datetime.utcnow()
            await db.commit()
            await db.refresh(job)
        return job

async def analyze_video_background(job_id: str, video_path: str, camera_id: str, location: str):
    async with AsyncSessionLocal() as db:
        await VideoService.update_job(db, job_id, "processing", 10.0)
        # Mock analysis
        await asyncio.sleep(5)
        await VideoService.update_job(db, job_id, "completed", 100.0)
"""

files[r"services\dashboard_service.py"] = """
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.event_service import EventService
from backend.database.models import Event, AlertLog
from sqlalchemy import func, select
from datetime import datetime

class DashboardService:
    @staticmethod
    async def get_summary(db: AsyncSession):
        stats = await EventService.get_statistics(db)
        alerts = await db.execute(select(func.count(AlertLog.id)).where(AlertLog.acknowledged == False))
        return {
            "total_events_today": stats['total_events'],
            "high_risk_events_today": stats['high_risk'],
            "critical_events_today": stats['critical'],
            "active_alerts": alerts.scalar() or 0
        }
        
    @staticmethod
    async def get_trends(db: AsyncSession):
        # mock trends
        return [{"date": str(datetime.now().date()), "risk_level": "HIGH", "count": 1}]
        
    @staticmethod
    async def get_location_stats(db: AsyncSession):
        # mock
        return [{"location": "Zone A", "events_count": 5, "high_risk_count": 2}]
        
    @staticmethod
    async def get_behaviour_stats(db: AsyncSession):
        # mock
        return [{"behaviour": "Speeding", "count": 3}]
"""

files[r"services\alert_service.py"] = """
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.database.models import AlertLog

class AlertService:
    @staticmethod
    async def create_alert(db: AsyncSession, event_id: str, alert_type: str):
        alert = AlertLog(event_id=event_id, alert_type=alert_type)
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        return alert

    @staticmethod
    async def get_recent_alerts(db: AsyncSession, limit: int = 50):
        result = await db.execute(select(AlertLog).order_by(AlertLog.sent_at.desc()).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def acknowledge_alert(db: AsyncSession, alert_id: str):
        result = await db.execute(select(AlertLog).where(AlertLog.id == alert_id))
        alert = result.scalar_one_or_none()
        if alert:
            alert.acknowledged = True
            await db.commit()
            await db.refresh(alert)
        return alert
"""

files[r"assistant\assistant.py"] = """
class WarehouseAssistant:
    def process_query(self, query: str):
        return {"response": f"I received your query: {query}. The backend assistant is currently in mock mode.", "data_used": {}}
"""

files[r"api\events.py"] = """
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from backend.database.connection import get_db
from backend.schemas.events import EventResponse, EventCreate, EventList, EventStats
from backend.services.event_service import EventService

router = APIRouter(prefix="/api/events", tags=["events"])

@router.get("", response_model=List[EventResponse])
async def list_events(
    risk_level: Optional[str] = None,
    event_type: Optional[str] = None,
    location: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    return await EventService.get_events(db, risk_level=risk_level)

@router.get("/high-risk", response_model=List[EventResponse])
async def high_risk_events(db: AsyncSession = Depends(get_db)):
    return await EventService.get_high_risk_events(db)

@router.get("/today", response_model=List[EventResponse])
async def today_events(db: AsyncSession = Depends(get_db)):
    return await EventService.get_today_events(db)

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
        raise HTTPException(status_code=404, detail="Event not found")
    return event
"""

files[r"api\video.py"] = """
from fastapi import APIRouter, Depends, BackgroundTasks, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from backend.database.connection import get_db
from backend.schemas.video import VideoUploadResponse, VideoJobStatus
from backend.services.video_service import VideoService, analyze_video_background
import shutil
import os

router = APIRouter(prefix="/api/video", tags=["video"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    job = await VideoService.create_job(db, file_path)
    return VideoUploadResponse(job_id=job.job_id, status="pending", message="Video uploaded successfully")

@router.post("/analyze")
async def analyze_video(
    background_tasks: BackgroundTasks,
    job_id: str = Form(...),
    camera_id: str = Form(...),
    location: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    job = await VideoService.get_job_status(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    background_tasks.add_task(analyze_video_background, job.job_id, job.video_path, camera_id, location)
    return {"message": "Analysis started in background"}

@router.get("/status/{job_id}", response_model=VideoJobStatus)
async def get_status(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await VideoService.get_job_status(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return VideoJobStatus(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        events_count=job.events_count,
        error_message=job.error_message
    )

@router.get("/list")
async def list_videos(db: AsyncSession = Depends(get_db)):
    return await VideoService.get_all_jobs(db)
"""

files[r"api\dashboard.py"] = """
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.connection import get_db
from backend.schemas.dashboard import DashboardSummary, RiskTrend, BehaviourStats, LocationStats
from backend.services.dashboard_service import DashboardService
from typing import List

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/summary", response_model=DashboardSummary)
async def get_summary(db: AsyncSession = Depends(get_db)):
    return await DashboardService.get_summary(db)

@router.get("/trends", response_model=List[RiskTrend])
async def get_trends(db: AsyncSession = Depends(get_db)):
    return await DashboardService.get_trends(db)

@router.get("/locations", response_model=List[LocationStats])
async def get_locations(db: AsyncSession = Depends(get_db)):
    return await DashboardService.get_location_stats(db)

@router.get("/behaviours", response_model=List[BehaviourStats])
async def get_behaviours(db: AsyncSession = Depends(get_db)):
    return await DashboardService.get_behaviour_stats(db)
"""

files[r"api\alerts.py"] = """
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.connection import get_db
from backend.services.alert_service import AlertService

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

@router.get("/recent")
async def get_recent(db: AsyncSession = Depends(get_db)):
    return await AlertService.get_recent_alerts(db)

@router.post("/{alert_id}/acknowledge")
async def acknowledge(alert_id: str, db: AsyncSession = Depends(get_db)):
    alert = await AlertService.acknowledge_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Acknowledged"}
"""

files[r"api\assistant.py"] = """
from fastapi import APIRouter
from backend.schemas.assistant import AssistantQuery, AssistantResponse
from backend.assistant.assistant import WarehouseAssistant

router = APIRouter(prefix="/api/assistant", tags=["assistant"])
assistant_svc = WarehouseAssistant()

@router.post("/query", response_model=AssistantResponse)
async def query_assistant(req: AssistantQuery):
    res = assistant_svc.process_query(req.query)
    return AssistantResponse(**res)
"""

files[r"main.py"] = """
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from backend.database.connection import engine, Base
from backend.api import events, video, dashboard, alerts, assistant
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    os.makedirs("uploads", exist_ok=True)
    yield
    # Shutdown
    pass

app = FastAPI(title="AI Warehouse Intelligence", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="uploads"), name="static")

app.include_router(events.router)
app.include_router(video.router)
app.include_router(dashboard.router)
app.include_router(alerts.router)
app.include_router(assistant.router)

@app.get("/")
def root():
    return {"message": "AI Warehouse Intelligence API is running"}
"""

for path, content in files.items():
    full_path = os.path.join(base, path)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"Written {full_path}")
