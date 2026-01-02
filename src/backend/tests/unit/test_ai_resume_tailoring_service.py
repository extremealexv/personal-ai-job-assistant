"""Unit tests for AI resume tailoring service."""

import json
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_posting import JobPosting
from app.models.master_resume import MasterResume
from app.models.prompt_template import PromptTemplate
from app.models.resume_version import ResumeVersion
from app.models.user import User
from app.schemas.resume_version import ResumeVersionCreate
from app.services.ai_resume_tailoring_service import AIResumeTailoringService


@pytest.fixture
def ai_resume_service():
    """Create AI resume tailoring service instance."""
    return AIResumeTailoringService()


@pytest.fixture
async def sample_master_resume(db_session: AsyncSession, test_user: User) -> MasterResume:
    """Create sample master resume for testing."""
    resume = MasterResume(
        user_id=test_user.id,
        full_name="John Doe",
        email="john.doe@example.com",
        phone="+1-234-567-8900",
        location="San Francisco, CA",
        summary="Experienced backend engineer with 10+ years building scalable systems",
        raw_text="Full resume text here...",
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
        company_name="TechCorp Inc.",
        job_title="Senior Backend Engineer",
        job_url="https://techcorp.com/careers/senior-backend-engineer",
        job_description="""
        We are looking for a Senior Backend Engineer with:
        - 5+ years of Python experience
        - Expertise in FastAPI and Django
        - Strong system design skills
        - Experience with PostgreSQL and Redis
        - Cloud infrastructure experience (AWS/GCP)
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
    """Create sample prompt template for testing."""
    prompt = PromptTemplate(
        user_id=test_user.id,
        task_type="resume_tailor",
        role_type="backend_engineer",
        name="Backend Engineer Resume Tailoring",
        prompt_text="""
        Tailor this resume for the job posting.
        
        Master Resume:
        {master_resume}
        
        Job Description:
        {job_description}
        
        Company: {company_name}
        
        Return ONLY valid JSON with modifications.
        """,
        is_active=True,
    )
    db_session.add(prompt)
    await db_session.commit()
    await db_session.refresh(prompt)
    return prompt


@pytest.mark.asyncio
class TestAIResumeTailoringService:
    """Test AI resume tailoring service."""

    async def test_get_or_create_default_prompt_exists(
        self,
        db_session: AsyncSession,
        ai_resume_service: AIResumeTailoringService,
        test_user: User,
        sample_prompt_template: PromptTemplate,
    ):
        """Test getting existing default prompt template."""
        prompt = await ai_resume_service._get_or_create_default_prompt(
            db_session, test_user.id, "backend_engineer"
        )

        assert prompt is not None
        assert prompt.task_type == "resume_tailor"
        assert prompt.role_type == "backend_engineer"
        assert prompt.is_active is True

    async def test_get_or_create_default_prompt_creates_new(
        self,
        db_session: AsyncSession,
        ai_resume_service: AIResumeTailoringService,
        test_user: User,
    ):
        """Test creating default prompt template when none exists."""
        prompt = await ai_resume_service._get_or_create_default_prompt(
            db_session, test_user.id, "data_scientist"
        )

        assert prompt is not None
        assert prompt.task_type == "resume_tailor"
        assert prompt.role_type == "data_scientist"
        assert prompt.is_active is True
        assert "master_resume" in prompt.prompt_text
        assert "job_description" in prompt.prompt_text

    async def test_create_resume_summary(
        self,
        ai_resume_service: AIResumeTailoringService,
        sample_master_resume: MasterResume,
    ):
        """Test creating resume summary from master resume."""
        summary = ai_resume_service._create_resume_summary(sample_master_resume)

        assert isinstance(summary, dict)
        assert "personal_info" in summary
        assert summary["personal_info"]["full_name"] == "John Doe"
        assert summary["personal_info"]["email"] == "john.doe@example.com"
        assert "work_experience" in summary
        assert "education" in summary
        assert "skills" in summary

    async def test_extract_json_from_response_clean_json(
        self, ai_resume_service: AIResumeTailoringService
    ):
        """Test extracting JSON from clean JSON response."""
        response = '{"modifications": {"summary": "Updated summary"}}'
        result = ai_resume_service._extract_json_from_response(response)

        assert isinstance(result, dict)
        assert "modifications" in result
        assert result["modifications"]["summary"] == "Updated summary"

    async def test_extract_json_from_response_markdown_block(
        self, ai_resume_service: AIResumeTailoringService
    ):
        """Test extracting JSON from markdown code block."""
        response = """```json
{
  "modifications": {
    "summary": "Updated summary"
  }
}
```"""
        result = ai_resume_service._extract_json_from_response(response)

        assert isinstance(result, dict)
        assert "modifications" in result
        assert result["modifications"]["summary"] == "Updated summary"

    async def test_extract_json_from_response_markdown_block_flexible_whitespace(
        self, ai_resume_service: AIResumeTailoringService
    ):
        """Test extracting JSON from markdown block with flexible whitespace."""
        # Test with various whitespace patterns
        test_cases = [
            "```json\n{\"key\": \"value\"}\n```",  # Standard
            "```json {\"key\": \"value\"} ```",  # No newlines
            "```json\n\n{\"key\": \"value\"}\n\n```",  # Multiple newlines
            "```json    {\"key\": \"value\"}    ```",  # Spaces
        ]

        for response in test_cases:
            result = ai_resume_service._extract_json_from_response(response)
            assert isinstance(result, dict)
            assert result["key"] == "value"

    async def test_extract_json_from_response_fallback_pattern(
        self, ai_resume_service: AIResumeTailoringService
    ):
        """Test fallback JSON extraction when no markdown block."""
        response = 'Here is the result: {"modifications": {"summary": "Test"}}'
        result = ai_resume_service._extract_json_from_response(response)

        assert isinstance(result, dict)
        assert "modifications" in result

    async def test_extract_json_from_response_invalid_json(
        self, ai_resume_service: AIResumeTailoringService
    ):
        """Test handling invalid JSON in response."""
        response = "This is not JSON at all"
        result = ai_resume_service._extract_json_from_response(response)

        # Should return error dict instead of raising exception
        assert isinstance(result, dict)
        assert "error" in result or "modifications" in result

    async def test_validate_and_sanitize_modifications_valid(
        self, ai_resume_service: AIResumeTailoringService
    ):
        """Test validating valid modifications."""
        modifications = {
            "summary": "Updated professional summary",
            "work_experience": [
                {
                    "company": "TechCorp",
                    "title": "Senior Engineer",
                    "achievements": ["Led team of 5", "Reduced latency by 40%"],
                }
            ],
            "skills": ["Python", "FastAPI", "PostgreSQL"],
        }

        result = ai_resume_service._validate_and_sanitize_modifications(modifications)
        assert isinstance(result, dict)
        assert "summary" in result

    async def test_validate_and_sanitize_modifications_empty(
        self, ai_resume_service: AIResumeTailoringService
    ):
        """Test handling empty modifications."""
        modifications = {}
        result = ai_resume_service._validate_and_sanitize_modifications(modifications)
        assert isinstance(result, dict)

    async def test_validate_and_sanitize_modifications_invalid_structure(
        self, ai_resume_service: AIResumeTailoringService
    ):
        """Test handling invalid modification structure."""
        modifications = "not a dict"
        result = ai_resume_service._validate_and_sanitize_modifications(modifications)
        # Should handle gracefully
        assert result is not None

    @pytest.mark.asyncio
    async def test_tailor_resume_creates_version(
        self,
        db_session: AsyncSession,
        ai_resume_service: AIResumeTailoringService,
        test_user: User,
        sample_master_resume: MasterResume,
        sample_job_posting: JobPosting,
        sample_prompt_template: PromptTemplate,
        monkeypatch,
    ):
        """Test that tailor_resume creates a resume version."""
        # Mock the AI provider to return a controlled response
        async def mock_tailor_resume(*args, **kwargs):
            class MockResponse:
                content = json.dumps(
                    {
                        "modifications": {
                            "summary": "Experienced backend engineer specializing in Python and FastAPI",
                            "skills": ["Python", "FastAPI", "PostgreSQL", "Redis"],
                        }
                    }
                )

            return MockResponse()

        # Patch the AI provider's tailor_resume method
        from app.services import ai_resume_tailoring_service

        original_provider = ai_resume_service._ai_provider
        mock_provider = type("MockProvider", (), {"tailor_resume": mock_tailor_resume})()
        monkeypatch.setattr(ai_resume_service, "_ai_provider", mock_provider)

        # Create tailoring request
        request = ResumeVersionCreate(
            version_name="TechCorp - Senior Backend Engineer",
            target_role="Senior Backend Engineer",
            target_company="TechCorp Inc.",
        )

        # Execute
        try:
            version = await ai_resume_service.tailor_resume(
                db_session,
                test_user.id,
                sample_master_resume.id,
                sample_job_posting.id,
                request,
                prompt_template_id=sample_prompt_template.id,
            )

            # Verify
            assert version is not None
            assert isinstance(version, ResumeVersion)
            assert version.master_resume_id == sample_master_resume.id
            assert version.job_posting_id == sample_job_posting.id
            assert version.version_name == "TechCorp - Senior Backend Engineer"
            assert version.modifications is not None
            assert "summary" in version.modifications
        finally:
            # Restore original provider
            monkeypatch.setattr(ai_resume_service, "_ai_provider", original_provider)

    async def test_get_resume_version_by_id(
        self,
        db_session: AsyncSession,
        ai_resume_service: AIResumeTailoringService,
        test_user: User,
        sample_master_resume: MasterResume,
        sample_job_posting: JobPosting,
    ):
        """Test retrieving resume version by ID."""
        # Create a resume version first
        version = ResumeVersion(
            master_resume_id=sample_master_resume.id,
            job_posting_id=sample_job_posting.id,
            version_name="Test Version",
            target_role="Engineer",
            target_company="Test Corp",
            modifications={"summary": "Test"},
        )
        db_session.add(version)
        await db_session.commit()
        await db_session.refresh(version)

        # Retrieve it
        retrieved = await ai_resume_service.get_resume_version(
            db_session, version.id, test_user.id
        )

        assert retrieved is not None
        assert retrieved.id == version.id
        assert retrieved.version_name == "Test Version"

    async def test_get_resume_version_not_found(
        self,
        db_session: AsyncSession,
        ai_resume_service: AIResumeTailoringService,
        test_user: User,
    ):
        """Test retrieving non-existent resume version."""
        fake_id = uuid4()
        version = await ai_resume_service.get_resume_version(db_session, fake_id, test_user.id)
        assert version is None

    async def test_list_resume_versions(
        self,
        db_session: AsyncSession,
        ai_resume_service: AIResumeTailoringService,
        test_user: User,
        sample_master_resume: MasterResume,
        sample_job_posting: JobPosting,
    ):
        """Test listing all resume versions."""
        # Create multiple versions
        for i in range(3):
            version = ResumeVersion(
                master_resume_id=sample_master_resume.id,
                job_posting_id=sample_job_posting.id,
                version_name=f"Version {i}",
                target_role="Engineer",
                target_company="Test Corp",
                modifications={},
            )
            db_session.add(version)

        await db_session.commit()

        # List versions
        versions = await ai_resume_service.list_resume_versions(
            db_session, test_user.id, sample_master_resume.id
        )

        assert len(versions) == 3
        assert all(isinstance(v, ResumeVersion) for v in versions)
