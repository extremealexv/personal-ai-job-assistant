"""Unit tests for AI cover letter generation service."""

import json
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application
from app.models.cover_letter import CoverLetter
from app.models.job_posting import JobPosting
from app.models.master_resume import MasterResume
from app.models.prompt_template import PromptTemplate
from app.models.resume_version import ResumeVersion
from app.models.user import User
from app.schemas.cover_letter import CoverLetterGenerate
from app.services.ai_cover_letter_service import AICoverLetterService


@pytest.fixture
def ai_cover_letter_service():
    """Create AI cover letter service instance."""
    return AICoverLetterService()


@pytest.fixture
async def sample_master_resume(db_session: AsyncSession, test_user: User) -> MasterResume:
    """Create sample master resume for testing."""
    resume = MasterResume(
        user_id=test_user.id,
        full_name="Jane Smith",
        email="jane.smith@example.com",
        phone="+1-555-123-4567",
        location="Seattle, WA",
        summary="Senior software engineer with 12+ years of experience in distributed systems",
        raw_text="Full resume content...",
    )
    db_session.add(resume)
    await db_session.commit()
    await db_session.refresh(resume)
    return resume


@pytest.fixture
async def sample_resume_version(
    db_session: AsyncSession, sample_master_resume: MasterResume
) -> ResumeVersion:
    """Create sample resume version for testing."""
    version = ResumeVersion(
        master_resume_id=sample_master_resume.id,
        version_name="VP Engineering Resume",
        target_role="VP of Engineering",
        target_company="InnovateTech",
        modifications={
            "summary": "Executive leader with 12+ years building and scaling engineering teams",
            "work_experience": [
                {
                    "company": "GlobalScale Inc.",
                    "title": "Director of Engineering",
                    "achievements": [
                        "Led architectural redesign supporting 500M daily transactions",
                        "Reduced operational latency by 30%",
                        "Improved system reliability from 99.9% to 99.999%",
                    ],
                }
            ],
        },
    )
    db_session.add(version)
    await db_session.commit()
    await db_session.refresh(version)
    return version


@pytest.fixture
async def sample_job_posting(db_session: AsyncSession, test_user: User) -> JobPosting:
    """Create sample job posting for testing."""
    job = JobPosting(
        user_id=test_user.id,
        company_name="InnovateTech Solutions",
        job_title="VP, Platform Engineering",
        job_url="https://innovatetech.com/careers/vp-engineering",
        job_description="""
        We are seeking a VP of Platform Engineering to lead our infrastructure team.
        
        Responsibilities:
        - Lead a team of 50+ engineers
        - Drive technical strategy for cloud infrastructure
        - Scale systems to support millions of users
        - Collaborate with product and business leaders
        
        Requirements:
        - 10+ years of software engineering experience
        - 5+ years in leadership roles
        - Expertise in distributed systems and cloud platforms
        - Strong communication and stakeholder management skills
        """,
        location="Seattle, WA",
        employment_type="Full-time",
        status="saved",
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)
    return job


@pytest.fixture
async def sample_application(
    db_session: AsyncSession,
    test_user: User,
    sample_job_posting: JobPosting,
    sample_resume_version: ResumeVersion,
) -> Application:
    """Create sample application for testing."""
    application = Application(
        user_id=test_user.id,
        job_posting_id=sample_job_posting.id,
        resume_version_id=sample_resume_version.id,
        status="draft",
    )
    db_session.add(application)
    await db_session.commit()
    await db_session.refresh(application)
    return application


@pytest.fixture
async def sample_prompt_template(db_session: AsyncSession, test_user: User) -> PromptTemplate:
    """Create sample prompt template for cover letters."""
    prompt = PromptTemplate(
        user_id=test_user.id,
        task_type="cover_letter",
        role_type="executive",
        name="Executive Cover Letter Template",
        prompt_text="""
        Generate an executive-level cover letter.
        
        Resume Summary:
        {resume_summary}
        
        Job Description:
        {job_description}
        
        Company: {company_name}
        Position: {job_title}
        
        Create a persuasive, personalized cover letter.
        """,
        is_active=True,
    )
    db_session.add(prompt)
    await db_session.commit()
    await db_session.refresh(prompt)
    return prompt


@pytest.mark.asyncio
class TestAICoverLetterService:
    """Test AI cover letter generation service."""

    async def test_get_or_create_default_prompt_exists(
        self,
        db_session: AsyncSession,
        ai_cover_letter_service: AICoverLetterService,
        test_user: User,
        sample_prompt_template: PromptTemplate,
    ):
        """Test getting existing default prompt template."""
        prompt = await ai_cover_letter_service._get_or_create_default_prompt(
            db_session, test_user.id, "executive"
        )

        assert prompt is not None
        assert prompt.task_type == "cover_letter"
        assert prompt.role_type == "executive"
        assert prompt.is_active is True

    async def test_get_or_create_default_prompt_creates_new(
        self,
        db_session: AsyncSession,
        ai_cover_letter_service: AICoverLetterService,
        test_user: User,
    ):
        """Test creating default prompt template when none exists."""
        prompt = await ai_cover_letter_service._get_or_create_default_prompt(
            db_session, test_user.id, "technical"
        )

        assert prompt is not None
        assert prompt.task_type == "cover_letter"
        assert prompt.role_type == "technical"
        assert prompt.is_active is True
        assert "resume_summary" in prompt.prompt_text
        assert "job_description" in prompt.prompt_text

    async def test_create_resume_summary_from_version(
        self,
        ai_cover_letter_service: AICoverLetterService,
        sample_resume_version: ResumeVersion,
    ):
        """Test creating resume summary from resume version."""
        summary = ai_cover_letter_service._create_resume_summary(sample_resume_version)

        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "Executive leader" in summary or "VP Engineering" in summary

    async def test_create_resume_summary_with_modifications(
        self,
        ai_cover_letter_service: AICoverLetterService,
        sample_resume_version: ResumeVersion,
    ):
        """Test resume summary includes modifications."""
        summary = ai_cover_letter_service._create_resume_summary(sample_resume_version)

        # Should include content from modifications
        assert "GlobalScale Inc." in summary or "Director of Engineering" in summary

    async def test_extract_content_from_response_clean_text(
        self, ai_cover_letter_service: AICoverLetterService
    ):
        """Test extracting content from clean text response."""
        response = "Dear Hiring Manager,\n\nI am excited to apply for this position..."
        result = ai_cover_letter_service._extract_content_from_response(response)

        assert isinstance(result, str)
        assert "Dear Hiring Manager" in result

    async def test_extract_content_from_response_markdown_block(
        self, ai_cover_letter_service: AICoverLetterService
    ):
        """Test extracting content from markdown code block."""
        response = """```
Dear Hiring Manager,

I am writing to express my interest...

Best regards,
Jane Smith
```"""
        result = ai_cover_letter_service._extract_content_from_response(response)

        assert isinstance(result, str)
        assert "Dear Hiring Manager" in result
        assert "```" not in result  # Markdown should be removed

    async def test_extract_content_from_response_mixed_content(
        self, ai_cover_letter_service: AICoverLetterService
    ):
        """Test extracting content from response with surrounding text."""
        response = """Here is the cover letter:

Dear Hiring Manager,

I am excited to apply for this position.

Best regards,
Jane Smith

I hope this helps!"""
        result = ai_cover_letter_service._extract_content_from_response(response)

        assert isinstance(result, str)
        assert "Dear Hiring Manager" in result

    async def test_validate_and_clean_content_valid(
        self, ai_cover_letter_service: AICoverLetterService
    ):
        """Test validating valid cover letter content."""
        content = "Dear Hiring Manager,\n\nThis is a professional cover letter.\n\nBest regards,\nJane Smith"
        result = ai_cover_letter_service._validate_and_clean_content(content)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Dear Hiring Manager" in result

    async def test_validate_and_clean_content_too_short(
        self, ai_cover_letter_service: AICoverLetterService
    ):
        """Test handling content that is too short."""
        content = "Hello"
        result = ai_cover_letter_service._validate_and_clean_content(content)

        # Should either extend or handle gracefully
        assert isinstance(result, str)

    async def test_validate_and_clean_content_trims_whitespace(
        self, ai_cover_letter_service: AICoverLetterService
    ):
        """Test that content is trimmed of excess whitespace."""
        content = "\n\n\n   Dear Hiring Manager,\n\nLetter content here.\n\n\n   "
        result = ai_cover_letter_service._validate_and_clean_content(content)

        assert result.startswith("Dear")
        assert not result.startswith("\n")
        assert not result.endswith("   ")

    @pytest.mark.asyncio
    async def test_generate_cover_letter_creates_record(
        self,
        db_session: AsyncSession,
        ai_cover_letter_service: AICoverLetterService,
        test_user: User,
        sample_application: Application,
        sample_prompt_template: PromptTemplate,
        monkeypatch,
    ):
        """Test that generate_cover_letter creates a cover letter record."""
        # Mock the AI provider to return a controlled response
        async def mock_generate_cover_letter(*args, **kwargs):
            class MockResponse:
                content = """Dear Hiring Manager,

I am writing to express my strong interest in the VP, Platform Engineering position at InnovateTech Solutions.

With over 12 years of experience building and scaling distributed systems, I am confident in my ability to lead your engineering organization.

Best regards,
Jane Smith"""

            return MockResponse()

        # Patch the AI provider's generate_cover_letter method
        mock_provider = type(
            "MockProvider", (), {"generate_cover_letter": mock_generate_cover_letter}
        )()
        monkeypatch.setattr(ai_cover_letter_service, "_ai_provider", mock_provider)

        # Create generation request
        request = CoverLetterGenerate(
            application_id=sample_application.id,
            tone="professional",
        )

        # Execute
        try:
            cover_letter = await ai_cover_letter_service.generate_cover_letter(
                db_session,
                test_user.id,
                request.application_id,
                tone=request.tone,
                prompt_template_id=sample_prompt_template.id,
            )

            # Verify
            assert cover_letter is not None
            assert isinstance(cover_letter, CoverLetter)
            assert cover_letter.application_id == sample_application.id
            assert len(cover_letter.content) > 0
            assert "VP, Platform Engineering" in cover_letter.content
            assert cover_letter.is_active is True
            assert cover_letter.version_number == 1
        finally:
            pass  # No need to restore since we're mocking the service's internal provider

    async def test_get_cover_letter_by_id(
        self,
        db_session: AsyncSession,
        ai_cover_letter_service: AICoverLetterService,
        test_user: User,
        sample_application: Application,
    ):
        """Test retrieving cover letter by ID."""
        # Create a cover letter first
        cover_letter = CoverLetter(
            application_id=sample_application.id,
            content="Test cover letter content",
            version_number=1,
            is_active=True,
        )
        db_session.add(cover_letter)
        await db_session.commit()
        await db_session.refresh(cover_letter)

        # Retrieve it
        retrieved = await ai_cover_letter_service.get_cover_letter(
            db_session, cover_letter.id, test_user.id
        )

        assert retrieved is not None
        assert retrieved.id == cover_letter.id
        assert retrieved.content == "Test cover letter content"

    async def test_get_cover_letter_not_found(
        self,
        db_session: AsyncSession,
        ai_cover_letter_service: AICoverLetterService,
        test_user: User,
    ):
        """Test retrieving non-existent cover letter."""
        fake_id = uuid4()
        cover_letter = await ai_cover_letter_service.get_cover_letter(
            db_session, fake_id, test_user.id
        )
        assert cover_letter is None

    async def test_list_cover_letters_for_application(
        self,
        db_session: AsyncSession,
        ai_cover_letter_service: AICoverLetterService,
        test_user: User,
        sample_application: Application,
    ):
        """Test listing all cover letters for an application."""
        # Create multiple cover letter versions
        for i in range(3):
            cover_letter = CoverLetter(
                application_id=sample_application.id,
                content=f"Cover letter version {i + 1}",
                version_number=i + 1,
                is_active=(i == 2),  # Last one is active
            )
            db_session.add(cover_letter)

        await db_session.commit()

        # List cover letters
        cover_letters = await ai_cover_letter_service.list_cover_letters(
            db_session, test_user.id, sample_application.id
        )

        assert len(cover_letters) == 3
        assert all(isinstance(cl, CoverLetter) for cl in cover_letters)
        # Verify version numbers
        version_numbers = [cl.version_number for cl in cover_letters]
        assert sorted(version_numbers) == [1, 2, 3]

    async def test_regenerate_cover_letter_increments_version(
        self,
        db_session: AsyncSession,
        ai_cover_letter_service: AICoverLetterService,
        test_user: User,
        sample_application: Application,
        monkeypatch,
    ):
        """Test that regenerating creates a new version."""
        # Create initial cover letter
        initial_cl = CoverLetter(
            application_id=sample_application.id,
            content="Initial cover letter",
            version_number=1,
            is_active=True,
        )
        db_session.add(initial_cl)
        await db_session.commit()

        # Mock AI provider
        async def mock_generate_cover_letter(*args, **kwargs):
            class MockResponse:
                content = "Regenerated cover letter with new content"

            return MockResponse()

        mock_provider = type(
            "MockProvider", (), {"generate_cover_letter": mock_generate_cover_letter}
        )()
        monkeypatch.setattr(ai_cover_letter_service, "_ai_provider", mock_provider)

        # Regenerate
        new_cl = await ai_cover_letter_service.generate_cover_letter(
            db_session, test_user.id, sample_application.id, tone="enthusiastic"
        )

        # Verify new version created
        assert new_cl.version_number == 2
        assert new_cl.is_active is True
        assert "Regenerated" in new_cl.content

        # Verify old version deactivated
        await db_session.refresh(initial_cl)
        assert initial_cl.is_active is False
