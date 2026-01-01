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

from app.api.deps import get_db  # Import from deps where endpoints actually use it
from app.config import settings
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
    """Create database session for tests with transaction management.
    
    Uses nested transactions (savepoints) so data persists within test
    but rolls back after test completes.
    """
    connection = await test_engine.connect()
    transaction = await connection.begin()
    
    async_session = async_sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint"
    )
    
    async with async_session() as session:
        yield session
    
    await transaction.rollback()
    await connection.close()


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
    
    async with AsyncClient(app=app, base_url="http://test", follow_redirects=True) as ac:
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
    await db_session.commit()  # Commit so user is visible to all queries in this session
    await db_session.refresh(user)
    
    return user


@pytest.fixture
async def auth_headers(test_user) -> dict[str, str]:
    """Create authentication headers for test user with JWT token."""
    from app.core.security import create_access_token
    
    access_token = create_access_token(
        {"sub": test_user.email, "user_id": str(test_user.id)}
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def other_user_auth_headers(other_user) -> dict[str, str]:
    """Create authentication headers for other user with JWT token."""
    from app.core.security import create_access_token
    
    access_token = create_access_token(
        {"sub": other_user.email, "user_id": str(other_user.id)}
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def test_pdf_content() -> bytes:
    """Generate a minimal valid PDF for testing."""
    # Properly formatted PDF that PyPDF2 can parse
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
>>
endobj
4 0 obj
<<
/Length 53
>>
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
0000000068 00000 n 
0000000137 00000 n 
0000000366 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
470
%%EOF
"""
    return pdf_content


# ============================================================================
# Database Cleanup Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
async def reset_db(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Reset database before and after each test.
    
    This fixture runs automatically to ensure clean state and prevent constraint violations.
    """
    # Clean up before test
    await db_session.rollback()
    
    yield
    
    # Clean up after test - delete all data to prevent unique constraint violations
    from sqlalchemy import text
    
    try:
        # Delete in reverse foreign key dependency order
        await db_session.execute(text("DELETE FROM cover_letters"))
        await db_session.execute(text("DELETE FROM applications"))
        await db_session.execute(text("DELETE FROM job_postings"))
        await db_session.execute(text("DELETE FROM resume_versions"))
        await db_session.execute(text("DELETE FROM certifications"))
        await db_session.execute(text("DELETE FROM skills"))
        await db_session.execute(text("DELETE FROM education"))
        await db_session.execute(text("DELETE FROM work_experiences"))
        await db_session.execute(text("DELETE FROM master_resumes"))
        await db_session.execute(text("DELETE FROM users"))
        await db_session.commit()
    except Exception:
        # If cleanup fails, just rollback - don't break the test
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
    config.addinivalue_line("markers", "job_management: Job management tests")


# ============================================================================
# Job Posting Fixtures
# ============================================================================


@pytest.fixture
async def sample_job_posting(db_session: AsyncSession, test_user):
    """Create a sample job posting for testing.
    
    Returns:
        JobPosting ORM object
    """
    from app.models.job import JobPosting, JobSource, JobStatus
    
    job = JobPosting(
        user_id=test_user.id,
        company_name="TechCorp Inc",
        job_title="Senior Backend Engineer",
        job_url="https://techcorp.example.com/jobs/senior-backend-engineer",
        source=JobSource.MANUAL,
        location="San Francisco, CA",
        salary_range="$150k-$200k",
        employment_type="Full-time",
        remote_policy="Hybrid",
        job_description="We are seeking a Senior Backend Engineer to join our team...",
        requirements="5+ years Python experience, FastAPI, PostgreSQL",
        nice_to_have="Experience with Redis, Celery, Docker",
        interest_level=4,
        notes="Great company culture",
        extracted_keywords=["python", "fastapi", "postgresql", "redis", "docker"],
        status=JobStatus.SAVED
    )
    
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)
    
    return job


@pytest.fixture
async def multiple_job_postings(db_session: AsyncSession, test_user) -> list[dict]:
    """Create multiple job postings for testing pagination and filtering.
    
    Returns:
        List of dictionaries with job posting data
    """
    from app.models.job import JobPosting, JobSource, JobStatus
    
    jobs_data = [
        {
            "company_name": "TechCorp",
            "job_title": "Senior Backend Engineer",
            "status": JobStatus.SAVED,
            "interest_level": 5
        },
        {
            "company_name": "DataSoft",
            "job_title": "Python Developer",
            "status": JobStatus.APPLIED,
            "interest_level": 4
        },
        {
            "company_name": "CloudNine",
            "job_title": "Full Stack Engineer",
            "status": JobStatus.INTERVIEWING,
            "interest_level": 3
        },
        {
            "company_name": "StartupXYZ",
            "job_title": "Backend Developer",
            "status": JobStatus.SAVED,
            "interest_level": 2
        },
        {
            "company_name": "MegaCorp",
            "job_title": "Software Engineer",
            "status": JobStatus.REJECTED,
            "interest_level": 1
        }
    ]
    
    created_jobs = []
    for job_data in jobs_data:
        job = JobPosting(
            user_id=test_user.id,
            company_name=job_data["company_name"],
            job_title=job_data["job_title"],
            job_url=f"https://{job_data['company_name'].lower()}.com/jobs",
            source=JobSource.MANUAL,
            status=job_data["status"],
            interest_level=job_data["interest_level"],
            job_description=f"Job at {job_data['company_name']}",
            extracted_keywords=["python", "backend", "api"]
        )
        db_session.add(job)
        await db_session.flush()
        await db_session.refresh(job)
        
        created_jobs.append({
            "id": job.id,
            "company_name": job.company_name,
            "job_title": job.job_title,
            "status": job.status,
            "interest_level": job.interest_level
        })
    
    return created_jobs


# ============================================================================
# Application Fixtures
# ============================================================================

@pytest.fixture
async def sample_resume_version(db_session, test_user, sample_job_posting):
    """Create a sample resume version for testing."""
    from app.models.resume import MasterResume, ResumeVersion
    
    # Create a master resume first
    master_resume = MasterResume(
        user_id=test_user.id,
        original_filename="test_resume.pdf",
        full_name=test_user.full_name,
        email=test_user.email,
    )
    db_session.add(master_resume)
    await db_session.flush()
    await db_session.refresh(master_resume)
    
    # Create resume version
    resume_version = ResumeVersion(
        master_resume_id=master_resume.id,
        job_posting_id=sample_job_posting.id,  # sample_job_posting is now an ORM object
        version_name="Tailored Resume for Test Job",
        target_role="Backend Engineer",
        target_company=sample_job_posting.company_name,
        modifications={"skills": ["Python", "FastAPI", "PostgreSQL"]},
    )
    db_session.add(resume_version)
    await db_session.commit()
    await db_session.refresh(resume_version)
    return resume_version


@pytest.fixture
async def sample_application(db_session, test_user, sample_job_posting, sample_resume_version):
    """Create a single application for testing."""
    from app.models.job import Application, ApplicationStatus
    
    application = Application(
        user_id=test_user.id,
        job_posting_id=sample_job_posting.id,  # sample_job_posting is now an ORM object
        resume_version_id=sample_resume_version.id,
        status=ApplicationStatus.DRAFT,
        submission_method="manual",
    )
    db_session.add(application)
    await db_session.commit()
    await db_session.refresh(application)
    return application


@pytest.fixture
async def multiple_applications(db_session, test_user, multiple_job_postings):
    """Create multiple applications with various statuses."""
    from app.models.job import Application, ApplicationStatus
    from app.models.resume import MasterResume, ResumeVersion
    from datetime import datetime, timedelta
    
    # Create a master resume first
    master_resume = MasterResume(
        user_id=test_user.id,
        original_filename="test_resume.pdf",
        full_name=test_user.full_name,
        email=test_user.email,
    )
    db_session.add(master_resume)
    await db_session.flush()
    await db_session.refresh(master_resume)
    
    # Create resume versions for each job
    resume_versions = []
    for i, job_data in enumerate(multiple_job_postings):
        rv = ResumeVersion(
            master_resume_id=master_resume.id,  # Use actual master_resume ID
            job_posting_id=job_data["id"],
            version_name=f"Resume v{i+1}",
            target_role=job_data["job_title"],
            target_company=job_data["company_name"],
        )
        db_session.add(rv)
        await db_session.flush()
        await db_session.refresh(rv)
        resume_versions.append(rv)
    
    # Application statuses to create
    applications_data = [
        {"status": ApplicationStatus.DRAFT, "days_ago": 1},
        {"status": ApplicationStatus.SUBMITTED, "days_ago": 3},
        {"status": ApplicationStatus.SUBMITTED, "days_ago": 5},
        {"status": ApplicationStatus.PHONE_SCREEN, "days_ago": 7},
        {"status": ApplicationStatus.REJECTED, "days_ago": 10},
    ]
    
    created_applications = []
    for i, app_data in enumerate(applications_data):
        created_at = datetime.utcnow() - timedelta(days=app_data["days_ago"])
        
        application = Application(
            user_id=test_user.id,
            job_posting_id=multiple_job_postings[i]["id"],
            resume_version_id=resume_versions[i].id,
            status=app_data["status"],
            submission_method="manual",
            submitted_at=created_at if app_data["status"] != ApplicationStatus.DRAFT else None,
            created_at=created_at,
        )
        db_session.add(application)
        await db_session.flush()
        await db_session.refresh(application)
        created_applications.append(application)
    
    await db_session.commit()
    return created_applications


@pytest.fixture
async def other_user(db_session):
    """Create another user for testing authorization."""
    from app.models.user import User
    from app.core.security import get_password_hash
    
    other = User(
        email="other@example.com",
        password_hash=get_password_hash("password123"),
        full_name="Other User",
        is_active=True,
    )
    db_session.add(other)
    await db_session.commit()
    await db_session.refresh(other)
    return other


@pytest.fixture
async def other_user_job(db_session, other_user):
    """Create a job posting for the other user."""
    from app.models.job import JobPosting, JobStatus
    
    job = JobPosting(
        user_id=other_user.id,
        company_name="Other Company",
        job_title="Other Role",
        job_url="https://example.com/other-job",
        status=JobStatus.SAVED,
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)
    return job


@pytest.fixture
async def other_user_application(db_session, other_user, other_user_job, sample_resume_version):
    """Create an application for the other user."""
    from app.models.job import Application, ApplicationStatus
    
    app = Application(
        user_id=other_user.id,
        job_posting_id=other_user_job.id,
        resume_version_id=sample_resume_version.id,
        status=ApplicationStatus.SUBMITTED,
    )
    db_session.add(app)
    await db_session.commit()
    await db_session.refresh(app)
    return app


# ================================================================================
# Cover Letter Fixtures
# ================================================================================


@pytest.fixture
async def sample_cover_letter(db_session, sample_application):
    """Create a single cover letter for testing."""
    from app.models.job import CoverLetter
    
    cover_letter = CoverLetter(
        application_id=sample_application.id,
        content="Dear Hiring Manager,\n\nI am excited to apply for this position. With over 10 years of experience in software development and a proven track record of delivering high-quality solutions, I am confident I would be an excellent addition to your team.",
        version_number=1,
        is_active=True,
        ai_model_used="gpt-4",
    )
    db_session.add(cover_letter)
    await db_session.commit()
    await db_session.refresh(cover_letter)
    return cover_letter


@pytest.fixture
async def multiple_cover_letter_versions(db_session, sample_application):
    """Create multiple versions of cover letters for testing."""
    from app.models.job import CoverLetter
    
    versions = []
    
    # Version 1 - Active
    v1 = CoverLetter(
        application_id=sample_application.id,
        content="Dear Hiring Manager,\n\nFirst version of cover letter expressing my strong interest in this position and outlining my relevant experience and qualifications.",
        version_number=1,
        is_active=True,
        ai_model_used="gpt-4",
    )
    db_session.add(v1)
    versions.append(v1)
    
    # Version 2 - Inactive
    v2 = CoverLetter(
        application_id=sample_application.id,
        content="Dear Hiring Manager,\n\nUpdated version with new information highlighting my recent achievements and technical skills that align perfectly with your requirements.",
        version_number=2,
        is_active=False,
        ai_model_used="gpt-4",
    )
    db_session.add(v2)
    versions.append(v2)
    
    await db_session.commit()
    for v in versions:
        await db_session.refresh(v)
    
    return versions
