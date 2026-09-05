"""
Database session management for AI Warehouse Intelligence.
Supports async SQLAlchemy for FastAPI and sync fallback for CLI/scripts.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, Session

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./warehouse.db")
SYNC_DATABASE_URL = os.environ.get("SYNC_DATABASE_URL", DATABASE_URL.replace("+aiosqlite", ""))

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)
SyncSessionLocal = sessionmaker(sync_engine, class_=Session, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    """FastAPI dependency for async DB session."""
    async with AsyncSessionLocal() as session:
        yield session


def get_sync_db():
    """Sync session generator for CLI tools."""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """Initialize tables asynchronously."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def init_sync_db():
    """Initialize tables synchronously."""
    Base.metadata.create_all(bind=sync_engine)
