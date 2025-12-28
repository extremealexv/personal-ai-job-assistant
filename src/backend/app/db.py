"""Database configuration and session management."""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import event, pool, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session

from app.config import settings
from app.models.base import Base


# Create async engine
engine: AsyncEngine = create_async_engine(
    settings.database_async_url,
    echo=settings.debug,  # Log SQL queries in debug mode
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,  # Number of connections to maintain
    max_overflow=10,  # Maximum overflow connections
    pool_recycle=3600,  # Recycle connections after 1 hour
)


# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions.
    
    Usage in FastAPI endpoints:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            users = result.scalars().all()
            return users
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database - create all tables.
    
    WARNING: This should only be used for development/testing.
    In production, use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        # Import all models to ensure they're registered
        from app import models  # noqa: F401
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully")


async def drop_db() -> None:
    """Drop all database tables.
    
    WARNING: This will delete all data! Use with caution.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("🗑️  Database tables dropped")


async def check_db_connection() -> bool:
    """Check if database connection is working.
    
    Returns:
        True if connection is successful, False otherwise.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


# Connection event listeners
@event.listens_for(pool.Pool, "connect")
def set_search_path(dbapi_conn: Any, connection_record: Any) -> None:
    """Set PostgreSQL search path on new connections."""
    existing_autocommit = dbapi_conn.autocommit
    dbapi_conn.autocommit = True
    cursor = dbapi_conn.cursor()
    cursor.execute("SET search_path TO public")
    cursor.close()
    dbapi_conn.autocommit = existing_autocommit


@event.listens_for(pool.Pool, "checkout")
def ping_connection(dbapi_conn: Any, connection_record: Any, connection_proxy: Any) -> None:
    """Ping connection on checkout to ensure it's alive."""
    cursor = dbapi_conn.cursor()
    try:
        cursor.execute("SELECT 1")
    except Exception:
        # Connection is dead, raise error to get a new one
        raise pool.exc.DisconnectionError()
    finally:
        cursor.close()


# Sync engine for Alembic migrations
def get_sync_engine() -> Any:
    """Get synchronous engine for Alembic migrations.
    
    Alembic doesn't fully support async engines yet,
    so we need a sync engine for migrations.
    """
    from sqlalchemy import create_engine
    
    # Convert async URL to sync URL
    sync_url = settings.database_url
    
    return create_engine(
        sync_url,
        echo=settings.debug,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600,
    )


def get_sync_session() -> Session:
    """Get synchronous session for scripts and migrations."""
    from sqlalchemy.orm import sessionmaker
    
    sync_engine = get_sync_engine()
    SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
    return SyncSessionLocal()
