"""Integration tests for AI cover letter generation API endpoints."""

import json
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application
from app.models.cover_letter import CoverLetter
from app.models.job_posting import JobPosting
from app.models.master_resume import MasterResume
from app.models.prompt_template import PromptTemplate
from app.models.resume_version import ResumeVersion
from app.models.user import User


@pytest.fixture
async def sample_setup(
    db_session: AsyncSession, test_user: User
) -> tuple[MasterResume, ResumeVersion, JobPosting, Application]:
    """Create full application setup for testing."""
    # Create master resume
    resume = MasterResume(
        user_id=test_user.id,
        full_name="Alice Engineer",
        email="alice@example.com",
        summary="Engineering leader with 10 years experience",
    )
    db_session.add(resume)

    # Create job posting
    job = JobPosting(
        user_id=test_user.id,
        company_name="TechStart",
        job_title="Engineering Manager",
        job_url="https://techstart.com/jobs/em",
        job_description="Looking for an experienced engineering manager...",
        status="saved",
    )
    db_session.add(job)
    await db_session.flush()

    # Create resume version
    version = ResumeVersion(
        master_resume_id=resume.id,
        job_posting_id=job.id,
        version_name="TechStart EM Resume",
        modifications={"summary": "Tailored summary"},
    )
    db_session.add(version)
    await db_session.flush()

    # Create application
    application = Application(
        user_id=test_user.id,
        job_posting_id=job.id,
        resume_version_id=version.id,
        status="draft",
    )
    db_session.add(application)
    await db_session.commit()

    await db_session.refresh(resume)
    await db_session.refresh(version)
    await db_session.refresh(job)
    await db_session.refresh(application)

    return resume, version, job, application


@pytest.fixture
async def sample_prompt_template(db_session: AsyncSession, test_user: User) -> PromptTemplate:
    """Create sample cover letter prompt template."""
    prompt = PromptTemplate(
        user_id=test_user.id,
        task_type="cover_letter",
        role_type="engineering_manager",
        name="Engineering Manager Cover Letter",
        prompt_text="""
        Generate cover letter for:
        Resume: {resume_summary}
        Job: {job_description}
        Company: {company_name}
        Role: {job_title}
        """,
        is_active=True,
    )
    db_session.add(prompt)
    await db_session.commit()
    await db_session.refresh(prompt)
    return prompt


@pytest.mark.asyncio
class TestAICoverLetterAPI:
    """Test AI cover letter generation API endpoints."""

    async def test_generate_cover_letter_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_setup: tuple,
        monkeypatch,
    ):
        """Test successful cover letter generation via API."""
        _, _, _, application = sample_setup

        # Mock AI provider response
        async def mock_generate_cover_letter(*args, **kwargs):
            class MockResponse:
                content = """Dear Hiring Manager,

I am writing to express my interest in the Engineering Manager position at TechStart.

With 10 years of engineering leadership experience, I am confident in my ability to contribute to your team.

Best regards,
Alice Engineer"""

            return MockResponse()

        from app.services.ai_cover_letter_service import AICoverLetterService

        service = AICoverLetterService()
        mock_provider = type(
            "MockProvider", (), {"generate_cover_letter": mock_generate_cover_letter}
        )()
        monkeypatch.setattr(service, "_ai_provider", mock_provider)

        # Make API request
        response = await async_client.post(
            "/api/v1/ai/cover-letter/generate",
            json={
                "application_id": str(application.id),
                "tone": "professional",
            },
            headers=auth_headers,
        )

        # Verify response
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["application_id"] == str(application.id)
        assert "Dear Hiring Manager" in data["content"]
        assert data["is_active"] is True
        assert data["version_number"] == 1

    async def test_generate_cover_letter_with_custom_tone(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_setup: tuple,
        monkeypatch,
    ):
        """Test cover letter generation with different tone."""
        _, _, _, application = sample_setup

        # Mock AI provider
        async def mock_generate_cover_letter(*args, **kwargs):
            class MockResponse:
                content = "Enthusiastic cover letter content!"

            return MockResponse()

        from app.services.ai_cover_letter_service import AICoverLetterService

        service = AICoverLetterService()
        mock_provider = type(
            "MockProvider", (), {"generate_cover_letter": mock_generate_cover_letter}
        )()
        monkeypatch.setattr(service, "_ai_provider", mock_provider)

        # Test different tones
        for tone in ["enthusiastic", "formal", "creative"]:
            response = await async_client.post(
                "/api/v1/ai/cover-letter/generate",
                json={
                    "application_id": str(application.id),
                    "tone": tone,
                },
                headers=auth_headers,
            )

            assert response.status_code == 201
            data = response.json()
            assert len(data["content"]) > 0

    async def test_generate_cover_letter_with_custom_prompt(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_setup: tuple,
        sample_prompt_template: PromptTemplate,
        monkeypatch,
    ):
        """Test cover letter generation with custom prompt template."""
        _, _, _, application = sample_setup

        # Mock AI provider
        async def mock_generate_cover_letter(*args, **kwargs):
            class MockResponse:
                content = "Custom template cover letter"

            return MockResponse()

        from app.services.ai_cover_letter_service import AICoverLetterService

        service = AICoverLetterService()
        mock_provider = type(
            "MockProvider", (), {"generate_cover_letter": mock_generate_cover_letter}
        )()
        monkeypatch.setattr(service, "_ai_provider", mock_provider)

        response = await async_client.post(
            "/api/v1/ai/cover-letter/generate",
            json={
                "application_id": str(application.id),
                "tone": "professional",
                "prompt_template_id": str(sample_prompt_template.id),
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["prompt_template_id"] == str(sample_prompt_template.id)

    async def test_generate_cover_letter_invalid_application(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test cover letter generation with invalid application ID."""
        fake_application_id = str(uuid4())

        response = await async_client.post(
            "/api/v1/ai/cover-letter/generate",
            json={
                "application_id": fake_application_id,
                "tone": "professional",
            },
            headers=auth_headers,
        )

        assert response.status_code in [404, 400]

    async def test_generate_cover_letter_missing_fields(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test cover letter generation with missing required fields."""
        response = await async_client.post(
            "/api/v1/ai/cover-letter/generate",
            json={},
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error

    async def test_generate_cover_letter_unauthorized(
        self,
        async_client: AsyncClient,
        sample_setup: tuple,
    ):
        """Test cover letter generation without authentication."""
        _, _, _, application = sample_setup

        response = await async_client.post(
            "/api/v1/ai/cover-letter/generate",
            json={
                "application_id": str(application.id),
                "tone": "professional",
            },
        )

        assert response.status_code == 401

    async def test_regenerate_cover_letter_increments_version(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        sample_setup: tuple,
        monkeypatch,
    ):
        """Test that regenerating creates a new version."""
        _, _, _, application = sample_setup

        # Create initial cover letter
        initial_cl = CoverLetter(
            application_id=application.id,
            content="Initial cover letter",
            version_number=1,
            is_active=True,
        )
        db_session.add(initial_cl)
        await db_session.commit()
        await db_session.refresh(initial_cl)

        # Mock AI provider
        async def mock_generate_cover_letter(*args, **kwargs):
            class MockResponse:
                content = "Regenerated cover letter v2"

            return MockResponse()

        from app.services.ai_cover_letter_service import AICoverLetterService

        service = AICoverLetterService()
        mock_provider = type(
            "MockProvider", (), {"generate_cover_letter": mock_generate_cover_letter}
        )()
        monkeypatch.setattr(service, "_ai_provider", mock_provider)

        # Generate new version
        response = await async_client.post(
            "/api/v1/ai/cover-letter/generate",
            json={
                "application_id": str(application.id),
                "tone": "professional",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["version_number"] == 2
        assert data["is_active"] is True

        # Verify old version was deactivated
        await db_session.refresh(initial_cl)
        assert initial_cl.is_active is False

    async def test_get_cover_letter_by_id(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        sample_setup: tuple,
    ):
        """Test retrieving cover letter by ID."""
        _, _, _, application = sample_setup

        # Create cover letter
        cover_letter = CoverLetter(
            application_id=application.id,
            content="Test cover letter content",
            version_number=1,
            is_active=True,
        )
        db_session.add(cover_letter)
        await db_session.commit()
        await db_session.refresh(cover_letter)

        # Retrieve via API
        response = await async_client.get(
            f"/api/v1/ai/cover-letter/{cover_letter.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(cover_letter.id)
        assert data["content"] == "Test cover letter content"

    async def test_get_cover_letter_not_found(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test retrieving non-existent cover letter."""
        fake_id = str(uuid4())

        response = await async_client.get(
            f"/api/v1/ai/cover-letter/{fake_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_list_cover_letters_for_application(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        sample_setup: tuple,
    ):
        """Test listing all cover letters for an application."""
        _, _, _, application = sample_setup

        # Create multiple cover letter versions
        for i in range(3):
            cover_letter = CoverLetter(
                application_id=application.id,
                content=f"Cover letter version {i + 1}",
                version_number=i + 1,
                is_active=(i == 2),
            )
            db_session.add(cover_letter)

        await db_session.commit()

        # List via API
        response = await async_client.get(
            "/api/v1/ai/cover-letter/list",
            params={"application_id": str(application.id)},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("version_number" in item for item in data)

    async def test_list_cover_letters_empty(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_setup: tuple,
    ):
        """Test listing cover letters when none exist."""
        _, _, _, application = sample_setup

        response = await async_client.get(
            "/api/v1/ai/cover-letter/list",
            params={"application_id": str(application.id)},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    async def test_update_cover_letter_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        sample_setup: tuple,
    ):
        """Test updating a cover letter."""
        _, _, _, application = sample_setup

        # Create cover letter
        cover_letter = CoverLetter(
            application_id=application.id,
            content="Original content",
            version_number=1,
            is_active=True,
        )
        db_session.add(cover_letter)
        await db_session.commit()
        await db_session.refresh(cover_letter)

        # Update via API
        response = await async_client.put(
            f"/api/v1/ai/cover-letter/{cover_letter.id}",
            json={"content": "Updated content"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated content"

    async def test_delete_cover_letter_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        sample_setup: tuple,
    ):
        """Test deleting a cover letter."""
        _, _, _, application = sample_setup

        # Create cover letter
        cover_letter = CoverLetter(
            application_id=application.id,
            content="To delete",
            version_number=1,
            is_active=True,
        )
        db_session.add(cover_letter)
        await db_session.commit()
        await db_session.refresh(cover_letter)

        # Delete via API
        response = await async_client.delete(
            f"/api/v1/ai/cover-letter/{cover_letter.id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify deletion
        get_response = await async_client.get(
            f"/api/v1/ai/cover-letter/{cover_letter.id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    async def test_activate_cover_letter_version(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        sample_setup: tuple,
    ):
        """Test activating a specific cover letter version."""
        _, _, _, application = sample_setup

        # Create multiple versions
        versions = []
        for i in range(3):
            cl = CoverLetter(
                application_id=application.id,
                content=f"Version {i + 1}",
                version_number=i + 1,
                is_active=(i == 2),  # Last one active
            )
            db_session.add(cl)
            versions.append(cl)

        await db_session.commit()
        for v in versions:
            await db_session.refresh(v)

        # Activate version 2 (middle one)
        response = await async_client.patch(
            f"/api/v1/ai/cover-letter/{versions[1].id}/activate",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True
        assert data["version_number"] == 2

        # Verify other versions are deactivated
        await db_session.refresh(versions[0])
        await db_session.refresh(versions[2])
        assert versions[0].is_active is False
        assert versions[2].is_active is False
