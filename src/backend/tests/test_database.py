"""Tests for database connection and session management."""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db, engine


@pytest.mark.integration
async def test_database_connection(db_session: AsyncSession):
    """Test that database connection works."""
    result = await db_session.execute(text("SELECT 1 as num"))
    row = result.fetchone()
    
    assert row is not None
    assert row[0] == 1


@pytest.mark.integration
async def test_database_transaction_rollback(db_session: AsyncSession):
    """Test that database transactions can be rolled back."""
    from app.models.user import User
    
    # Create user
    user = User(
        email="rollback@example.com",
        password_hash="hashed",
        full_name="Rollback Test",
    )
    db_session.add(user)
    await db_session.flush()
    
    # Rollback (fixture does this automatically)
    await db_session.rollback()
    
    # User should not exist after rollback
    result = await db_session.execute(
        text("SELECT email FROM users WHERE email = 'rollback@example.com'")
    )
    assert result.fetchone() is None


@pytest.mark.integration
async def test_database_query_execution(db_session: AsyncSession):
    """Test executing database queries."""
    # Execute query
    result = await db_session.execute(
        text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LIMIT 1")
    )
    row = result.fetchone()
    
    # Should have at least one table
    assert row is not None


@pytest.mark.integration
async def test_database_supports_jsonb(db_session: AsyncSession):
    """Test that database supports JSONB operations."""
    result = await db_session.execute(
        text("SELECT '{\"key\": \"value\"}'::jsonb as data")
    )
    row = result.fetchone()
    
    assert row is not None
    assert "key" in row[0]


@pytest.mark.integration
async def test_database_supports_uuid(db_session: AsyncSession):
    """Test that database supports UUID type."""
    result = await db_session.execute(
        text("SELECT gen_random_uuid() as id")
    )
    row = result.fetchone()
    
    assert row is not None
    assert len(str(row[0])) == 36  # UUID string length


@pytest.mark.integration
async def test_database_supports_enums(db_session: AsyncSession):
    """Test that database has custom enum types."""
    result = await db_session.execute(
        text(
            "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'experience_type') as exists"
        )
    )
    row = result.fetchone()
    
    assert row[0] is True  # experience_type enum exists


@pytest.mark.integration
async def test_database_has_required_tables(db_session: AsyncSession):
    """Test that all required tables exist."""
    required_tables = [
        "users",
        "master_resumes",
        "work_experiences",
        "education",
        "skills",
        "job_postings",
        "applications",
    ]
    
    for table_name in required_tables:
        result = await db_session.execute(
            text(
                f"SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                f"WHERE table_name = '{table_name}') as exists"
            )
        )
        row = result.fetchone()
        assert row[0] is True, f"Table {table_name} should exist"


@pytest.mark.integration
async def test_get_db_dependency():
    """Test get_db dependency works."""
    # get_db is an async generator
    db_gen = get_db()
    
    # Get session
    session = await db_gen.__anext__()
    
    assert isinstance(session, AsyncSession)
    
    # Clean up
    try:
        await db_gen.__anext__()
    except StopAsyncIteration:
        pass  # Expected


@pytest.mark.unit
def test_engine_is_configured():
    """Test that engine is properly configured."""
    assert engine is not None
    assert hasattr(engine, "url")
    assert hasattr(engine, "dispose")


@pytest.mark.integration
async def test_database_connection_pool():
    """Test database connection pooling works."""
    # Get multiple sessions
    db_gen1 = get_db()
    db_gen2 = get_db()
    
    session1 = await db_gen1.__anext__()
    session2 = await db_gen2.__anext__()
    
    # Both should be valid sessions
    assert isinstance(session1, AsyncSession)
    assert isinstance(session2, AsyncSession)
    
    # Clean up
    for gen in [db_gen1, db_gen2]:
        try:
            await gen.__anext__()
        except StopAsyncIteration:
            pass
