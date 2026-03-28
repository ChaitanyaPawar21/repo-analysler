"""
db/postgres.py - Async PostgreSQL Database Setup
=================================================
Configures SQLAlchemy async engine, session factory, and base model.
Uses connection pooling for production-grade performance.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Async Engine
# =============================================================================

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,    # Recycle connections after 1 hour
)


# =============================================================================
# Async Session Factory
# =============================================================================

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Avoid lazy-load issues in async context
)


# =============================================================================
# Declarative Base
# =============================================================================

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    All models should inherit from this base.
    """
    pass


# =============================================================================
# Database Initialization
# =============================================================================

async def init_db() -> None:
    """
    Create all tables defined by models that inherit from Base.
    In production, use Alembic migrations instead of create_all.
    """
    async with engine.begin() as conn:
        # Import all models here so they are registered with Base.metadata
        import models.repo  # noqa: F401
        import models.analysis  # noqa: F401

        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified")


# =============================================================================
# Dependency Injection
# =============================================================================

async def get_db_session() -> AsyncSession:
    """
    FastAPI dependency that provides a database session per request.
    Automatically handles commit/rollback and session cleanup.

    Usage in endpoints:
        async def my_endpoint(db: AsyncSession = Depends(get_db_session)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
