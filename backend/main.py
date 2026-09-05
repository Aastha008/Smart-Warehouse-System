"""
AI Warehouse Intelligence - FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.database.connection import engine, Base
from backend.api import events, video, dashboard, alerts, assistant
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Ensure required directories exist
    for d in ["uploads", "data/uploads", "data/processed", "data/frames"]:
        os.makedirs(d, exist_ok=True)

    yield
    # Shutdown - nothing to clean up


app = FastAPI(
    title="AI Warehouse Intelligence",
    description="AI-powered video intelligence for safer, damage-free warehouse operations",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(events.router)
app.include_router(video.router)
app.include_router(dashboard.router)
app.include_router(alerts.router)
app.include_router(assistant.router)

# Mount static files for uploaded videos and compiled production frontend
try:
    from fastapi.staticfiles import StaticFiles
    from starlette.responses import FileResponse
    os.makedirs("uploads", exist_ok=True)
    app.mount("/static", StaticFiles(directory="uploads"), name="static")
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

    frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
    if os.path.exists(frontend_dist):
        assets_dir = os.path.join(frontend_dist, "assets")
        if os.path.exists(assets_dir):
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
except Exception as e:
    pass


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "AI Warehouse Intelligence API is running", "version": "1.0.0"}


@app.get("/api/statistics")
@app.get("/statistics")
async def statistics_alias():
    """Alias for /api/events/statistics - convenience route."""
    from backend.database.connection import AsyncSessionLocal
    from backend.services.event_service import EventService

    async with AsyncSessionLocal() as db:
        stats = await EventService.get_statistics(db)
        return stats


@app.post("/assistant/query")
async def assistant_query_alias(req: assistant.AssistantQuery, db: assistant.AsyncSession = assistant.Depends(assistant.get_db)):
    """Alias for /api/assistant/query."""
    return await assistant.query_assistant(req, db)


# SPA catch-all route for production deployment
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    from starlette.responses import FileResponse
    from fastapi import HTTPException

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_dist, "index.html"))

    @app.get("/{full_path:path}")
    async def serve_spa_app(full_path: str):
        if full_path.startswith("api/") or full_path.startswith("uploads/") or full_path.startswith("static/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        target = os.path.join(frontend_dist, full_path)
        if os.path.isfile(target):
            return FileResponse(target)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    def root():
        """Fallback health check endpoint when frontend is not built."""
        return {"message": "AI Warehouse Intelligence API is running", "version": "1.0.0"}

