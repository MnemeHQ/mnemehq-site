"""
Database initialization for Mneme Audit M1.
"""
from __future__ import annotations

from app.db.models import Base
from app.db.session import engine


async def init_db() -> None:
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """Drop all tables (for testing)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)