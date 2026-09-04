"""
Database session management for Mneme Audit M1.

Supports both local development (NullPool) and production (QueuePool with connection pooling).
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool

from app.core.config import settings


def _create_engine():
    """Create async engine with appropriate pool configuration."""
    database_url = settings.resolved_database_url
    
    # Determine pool class based on environment
    if settings.DB_POOL_DISABLED or not settings.CLOUD_SQL_CONNECTION_NAME:
        # Local development or explicit disable -> NullPool
        pool_class = NullPool
        pool_kwargs = {}
    else:
        # Production (Cloud Run) -> QueuePool with sensible defaults
        pool_class = AsyncAdaptedQueuePool
        pool_kwargs = {
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
            "pool_timeout": settings.DB_POOL_TIMEOUT,
            "pool_recycle": settings.DB_POOL_RECYCLE,
            "pool_pre_ping": True,
        }

    return create_async_engine(
        database_url,
        echo=settings.DB_ECHO,
        poolclass=pool_class,
        **pool_kwargs,
    )


engine = _create_engine()

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database session."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for database session outside of FastAPI."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database - create tables if they don't exist."""
    from app.db.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
