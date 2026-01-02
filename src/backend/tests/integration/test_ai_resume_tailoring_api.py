"""Integration tests for AI resume tailoring API endpoints."""

import json
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_posting import JobPosting
from app.models.master_resume import MasterResume
from app.models.prompt_template import PromptTemplate
from app.models.resume_version import ResumeVersion
from app.models.user import User


@pytest.fixture
async def sample_master_resume(db_session: AsyncSession, test_user: User) -> MasterResume:
    """Create sample master resume for testing."""
    resume = MasterResume(
        user_id=test_user.id,
        full_name="John Developer",
        email="john.dev@example.com",
        phone="+1-987-654-3210",
        location="Austin, TX",
        summary="Full-stack engineer with 8 years of experience",
        raw_text="Resume content here...",
    )
    db_session.add(resume)
    await db_session.commit()
    await db_session.refresh(resume)
    return resume


@pytest.fixture
async def sample_job_posting(db_session: AsyncSession, test_user: User) -> JobPosting:
    """Create sample job posting for testing."""
    job = JobPosting(
        user_id=test_user.id,
        company_name="Startup Inc.",
        job_title="Lead Backend Engineer",
        job_url="https://startup.com/careers/lead-backend-engineer",
        job_description="""
        Seeking a Lead Backend Engineer with:
        - 5+ years Python/Go experience
        - Microservices architecture expertise
        - Strong API design skills
        - Experience with Kubernetes and cloud platforms
        """,
        location="Remote",
        employment_type="Full-time",
        status="saved",
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)
    return job


@pytest.fixture
async def sample_prompt_template(db_session: AsyncSession, test_user: User) -> PromptTemplate:
    """Create sample prompt template."""
    prompt = PromptTemplate(
        user_id=test_user.id,
        task_type="resume_tailor",
        role_type="backend_engineer",
        name="Test Resume Tailoring Prompt",
        prompt_text="""
        Tailor resume for job.
        Resume: {master_resume}
        Job: {job_description}
        Company: {company_name}
        Return JSON with modifications.
        """,
        is_active=True,
    )
    db_session.add(prompt)
    await db_session.commit()
    await db_session.refresh(prompt)
    return prompt


@pytest.mark.asyncio
class TestAIResumeTailoringAPI:
    """Test AI resume tailoring API endpoints."""

    async def test_tailor_resume_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User,
        sample_master_resume: MasterResume,
        sample_job_posting: JobPosting,
        sample_prompt_template: PromptTemplate,
        monkeypatch,
    ):
        """Test successful resume tailoring via API."""
        # Mock AI provider response
        async def mock_tailor_resume(*args, **kwargs):
            class MockResponse:
                content = json.dumps(
                    {
                        "modifications": {
                            "summary": "Lead backend engineer with 8 years building microservices",
                            "skills": ["Python", "Go", "Kubernetes", "Docker"],
                        }
                    }
                )

            return MockResponse()

        # Patch the Gemini provider (or whatever is configured)
        from app.services.ai_resume_tailoring_service import AIResumeTailoringService

        service = AIResumeTailoringService()
        mock_provider = type("MockProvider", (), {"tailor_resume": mock_tailor_resume})()
        monkeypatch.setattr(service, "_ai_provider", mock_provider)

        # Make API request
        response = await async_client.post(
            "/api/v1/ai/resume/tailor",
            json={
                "master_resume_id": str(sample_master_resume.id),
                "job_posting_id": str(sample_job_posting.id),
                "version_name": "Startup Inc - Lead Backend Engineer",
                "target_role": "Lead Backend Engineer",
                "target_company": "Startup Inc.",
            },
            headers=auth_headers,
        )

        # Verify response
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["version_name"] == "Startup Inc - Lead Backend Engineer"
        assert data["target_role"] == "Lead Backend Engineer"
        assert data["target_company"] == "Startup Inc."
        assert "modifications" in data
        assert data["master_resume_id"] == str(sample_master_resume.id)
        assert data["job_posting_id"] == str(sample_job_posting.id)

    async def test_tailor_resume_with_custom_prompt(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_master_resume: MasterResume,
        sample_job_posting: JobPosting,
        sample_prompt_template: PromptTemplate,
        monkeypatch,
    ):
        """Test resume tailoring with custom prompt template."""
        # Mock AI provider
        async def mock_tailor_resume(*args, **kwargs):
            class MockResponse:
                content = json.dumps({"modifications": {"summary": "Custom tailored summary"}})

            return MockResponse()

        from app.services.ai_resume_tailoring_service import AIResumeTailoringService

        service = AIResumeTailoringService()
        mock_provider = type("MockProvider", (), {"tailor_resume": mock_tailor_resume})()
        monkeypatch.setattr(service, "_ai_provider", mock_provider)

        # Make API request with prompt_template_id
        response = await async_client.post(
            "/api/v1/ai/resume/tailor",
            json={
                "master_resume_id": str(sample_master_resume.id),
                "job_posting_id": str(sample_job_posting.id),
                "version_name": "Custom Prompt Version",
                "prompt_template_id": str(sample_prompt_template.id),
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["prompt_template_id"] == str(sample_prompt_template.id)

    async def test_tailor_resume_invalid_master_resume(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_job_posting: JobPosting,
    ):
        """Test tailoring with invalid master resume ID."""
        fake_resume_id = str(uuid4())

        response = await async_client.post(
            "/api/v1/ai/resume/tailor",
            json={
                "master_resume_id": fake_resume_id,
                "job_posting_id": str(sample_job_posting.id),
                "version_name": "Test Version",
            },
            headers=auth_headers,
        )

        assert response.status_code in [404, 400]  # Not found or bad request

    async def test_tailor_resume_invalid_job_posting(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_master_resume: MasterResume,
    ):
        """Test tailoring with invalid job posting ID."""
        fake_job_id = str(uuid4())

        response = await async_client.post(
            "/api/v1/ai/resume/tailor",
            json={
                "master_resume_id": str(sample_master_resume.id),
                "job_posting_id": fake_job_id,
                "version_name": "Test Version",
            },
            headers=auth_headers,
        )

        assert response.status_code in [404, 400]

    async def test_tailor_resume_missing_required_fields(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test tailoring with missing required fields."""
        response = await async_client.post(
            "/api/v1/ai/resume/tailor",
            json={
                "version_name": "Incomplete Request",
            },
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error

    async def test_tailor_resume_unauthorized(
        self,
        async_client: AsyncClient,
        sample_master_resume: MasterResume,
        sample_job_posting: JobPosting,
    ):
        """Test tailoring without authentication."""
        response = await async_client.post(
            "/api/v1/ai/resume/tailor",
            json={
                "master_resume_id": str(sample_master_resume.id),
                "job_posting_id": str(sample_job_posting.id),
                "version_name": "Unauthorized Version",
            },
        )

        assert response.status_code == 401  # Unauthorized

    async def test_get_resume_version_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        sample_master_resume: MasterResume,
        sample_job_posting: JobPosting,
    ):
        """Test retrieving resume version by ID."""
        # Create a resume version
        version = ResumeVersion(
            master_resume_id=sample_master_resume.id,
            job_posting_id=sample_job_posting.id,
            version_name="Test Version",
            target_role="Engineer",
            target_company="Test Corp",
            modifications={"summary": "Test summary"},
        )
        db_session.add(version)
        await db_session.commit()
        await db_session.refresh(version)

        # Retrieve via API
        response = await async_client.get(
            f"/api/v1/ai/resume/versions/{version.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(version.id)
        assert data["version_name"] == "Test Version"

    async def test_get_resume_version_not_found(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test retrieving non-existent resume version."""
        fake_id = str(uuid4())

        response = await async_client.get(
            f"/api/v1/ai/resume/versions/{fake_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_list_resume_versions_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        sample_master_resume: MasterResume,
        sample_job_posting: JobPosting,
    ):
        """Test listing resume versions."""
        # Create multiple versions
        for i in range(3):
            version = ResumeVersion(
                master_resume_id=sample_master_resume.id,
                job_posting_id=sample_job_posting.id,
                version_name=f"Version {i + 1}",
                target_role="Engineer",
                modifications={},
            )
            db_session.add(version)

        await db_session.commit()

        # List via API
        response = await async_client.get(
            "/api/v1/ai/resume/versions",
            params={"master_resume_id": str(sample_master_resume.id)},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("version_name" in item for item in data)

    async def test_list_resume_versions_empty(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_master_resume: MasterResume,
    ):
        """Test listing resume versions when none exist."""
        response = await async_client.get(
            "/api/v1/ai/resume/versions",
            params={"master_resume_id": str(sample_master_resume.id)},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    async def test_delete_resume_version_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        sample_master_resume: MasterResume,
        sample_job_posting: JobPosting,
    ):
        """Test deleting a resume version."""
        # Create version
        version = ResumeVersion(
            master_resume_id=sample_master_resume.id,
            job_posting_id=sample_job_posting.id,
            version_name="To Delete",
            modifications={},
        )
        db_session.add(version)
        await db_session.commit()
        await db_session.refresh(version)

        # Delete via API
        response = await async_client.delete(
            f"/api/v1/ai/resume/versions/{version.id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify deletion
        get_response = await async_client.get(
            f"/api/v1/ai/resume/versions/{version.id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    async def test_update_resume_version_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        sample_master_resume: MasterResume,
        sample_job_posting: JobPosting,
    ):
        """Test updating a resume version."""
        # Create version
        version = ResumeVersion(
            master_resume_id=sample_master_resume.id,
            job_posting_id=sample_job_posting.id,
            version_name="Original Name",
            modifications={},
        )
        db_session.add(version)
        await db_session.commit()
        await db_session.refresh(version)

        # Update via API
        response = await async_client.put(
            f"/api/v1/ai/resume/versions/{version.id}",
            json={"version_name": "Updated Name", "target_role": "Senior Engineer"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["version_name"] == "Updated Name"
        assert data["target_role"] == "Senior Engineer"
