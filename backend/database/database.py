"""
Unified database access helper for AI Warehouse Intelligence.
Provides both async and sync context managers and query helpers.
"""
from contextlib import asynccontextmanager, contextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from backend.database.session import (
    AsyncSessionLocal,
    SyncSessionLocal,
    init_db,
    init_sync_db,
    Base,
    engine,
    sync_engine,
    get_db,
    get_sync_db,
)


class DatabaseManager:
    """Database manager supporting sync and async operations."""

    @staticmethod
    def get_sync_session() -> Session:
        """Get a new synchronous session."""
        return SyncSessionLocal()

    @staticmethod
    def get_async_session() -> AsyncSession:
        """Get a new asynchronous session."""
        return AsyncSessionLocal()

    @staticmethod
    async def init():
        """Initialize database tables asynchronously."""
        await init_db()

    @staticmethod
    def init_sync():
        """Initialize database tables synchronously."""
        init_sync_db()

    @staticmethod
    @asynccontextmanager
    async def async_session_scope():
        """Async context manager for DB session."""
        session = AsyncSessionLocal()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    @staticmethod
    @contextmanager
    def sync_session_scope():
        """Sync context manager for DB session."""
        session = SyncSessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
