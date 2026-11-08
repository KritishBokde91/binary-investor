"""SQLAlchemy 2.0 async engine and declarative base configuration."""

import os
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

DEFAULT_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/sheep_or_sleep"


class Base(AsyncAttrs, DeclarativeBase):
    """Base model class for SQLAlchemy 2.0 declarative models."""
    pass


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def get_async_engine(url: str | None = None):
    db_url = url or get_database_url()
    return create_async_engine(db_url, echo=False, future=True)


def get_async_session_maker(engine=None):
    eng = engine or get_async_engine()
    return async_sessionmaker(eng, expire_on_commit=False, class_=AsyncSession)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for yielding async database sessions."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        yield session
