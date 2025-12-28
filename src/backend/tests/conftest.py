"""Pytest configuration and shared fixtures."""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine, event, pool
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import get_db
from app.main import app
from app.models.base import Base

# Test database URL (use separate test database)
# Extract database name from URL and append _test
database_url = settings.database_url
database_async_url = settings.database_async_url

# For PostgreSQL URLs like postgresql://user:pass@host:port/dbname
if database_url and "/" in database_url:
    base_url, db_name = database_url.rsplit("/", 1)
    TEST_DATABASE_URL = f"{base_url}/{db_name}_test"
else:
    # Fallback: use environment variable or default
    TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://ai_job_user:your_password@localhost:5432/ai_job_assistant_test")

if database_async_url and "/" in database_async_url:
    base_url, db_name = database_async_url.rsplit("/", 1)
    TEST_DATABASE_ASYNC_URL = f"{base_url}/{db_name}_test"
else:
    # Fallback: use environment variable or default
    TEST_DATABASE_ASYNC_URL = os.getenv("TEST_DATABASE_ASYNC_URL", "postgresql+asyncpg://ai_job_user:your_password@localhost:5432/ai_job_assistant_test")


# ============================================================================
# Async Engine and Session Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create test database engine.
    
    Note: The test database must exist before running tests.
    Run 'python scripts/setup_test_db.py' to create it.
    """
    try:
        engine = create_async_engine(
            TEST_DATABASE_ASYNC_URL,
            echo=False,
            poolclass=pool.NullPool,  # No connection pooling for tests
        )
    except Exception as e:
        raise RuntimeError(
            f"Could not connect to test database: {TEST_DATABASE_ASYNC_URL}\n"
            f"Make sure it exists by running: python scripts/setup_test_db.py\n"
            f"Error: {e}"
        ) from e
    
    # Create all tables (in case they don't exist)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        await engine.dispose()
        raise RuntimeError(
            f"Could not create tables in test database.\n"
            f"Try running: python scripts/setup_test_db.py --drop\n"
            f"Error: {e}"
        ) from e
    
    yield engine
    
    # Cleanup: drop all tables after tests
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    except Exception:
        pass  # Ignore cleanup errors
    
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests.
    
    Each test gets a fresh session that's rolled back after the test.
    """
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


# ============================================================================
# FastAPI Client Fixtures
# ============================================================================


@pytest.fixture
def client(db_session: AsyncSession) -> Generator[TestClient, None, None]:
    """Create FastAPI test client with database session override."""
    
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing async endpoints."""
    
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


# ============================================================================
# Authentication Fixtures
# ============================================================================


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user with properly hashed password."""
    from app.models.user import User
    from app.core.security import get_password_hash
    
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("TestPassword123!"),
        full_name="Test User",
        is_active=True,
        email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user


@pytest.fixture
def auth_headers(test_user) -> dict[str, str]:
    """Create authentication headers for test user with JWT token."""
    from app.core.security import create_access_token
    
    access_token = create_access_token(
        {"sub": test_user.email, "user_id": str(test_user.id)}
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def test_pdf_content() -> bytes:
    """Generate a minimal valid PDF for testing."""
    # Minimal valid PDF structure
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Test Resume) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000214 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
308
%%EOF
"""
    return pdf_content


# ============================================================================
# Database Cleanup Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
async def reset_db(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Reset database before each test.
    
    This fixture runs automatically before each test to ensure clean state.
    """
    yield
    
    # Rollback any uncommitted changes
    await db_session.rollback()


# ============================================================================
# Pytest Configuration
# ============================================================================


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, no DB)")
    config.addinivalue_line("markers", "integration: Integration tests (with DB)")
    config.addinivalue_line("markers", "e2e: End-to-end tests (full workflow)")
    config.addinivalue_line("markers", "slow: Slow tests")
