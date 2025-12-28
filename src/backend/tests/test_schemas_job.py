"""Tests for job posting schemas."""

import pytest
from uuid import uuid4

from pydantic import ValidationError

from app.schemas.job import (
    JobPostingCreate,
    JobPostingUpdate,
    JobPostingResponse,
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
)


@pytest.mark.unit
def test_job_posting_create_valid():
    """Test creating valid job posting."""
    job = JobPostingCreate(
        company_name="TechCorp",
        job_title="Senior Backend Engineer",
        job_url="https://techcorp.com/jobs/123",
        job_description="We are looking for...",
        location="San Francisco, CA",
        interest_level=5,
    )
    
    assert job.company_name == "TechCorp"
    assert job.job_title == "Senior Backend Engineer"
    assert job.interest_level == 5


@pytest.mark.unit
def test_job_posting_missing_required():
    """Test job posting fails without required fields."""
    with pytest.raises(ValidationError):
        JobPostingCreate(company_name="TechCorp")


@pytest.mark.unit
def test_job_posting_invalid_url():
    """Test job posting fails with invalid URL."""
    with pytest.raises(ValidationError):
        JobPostingCreate(
            company_name="TechCorp",
            job_title="Engineer",
            job_url="not-a-valid-url",
        )


@pytest.mark.unit
def test_job_posting_interest_level_validation():
    """Test interest level must be between 1 and 5."""
    with pytest.raises(ValidationError):
        JobPostingCreate(
            company_name="TechCorp",
            job_title="Engineer",
            job_url="https://example.com",
            interest_level=10,  # Invalid - too high
        )


@pytest.mark.unit
def test_job_posting_update_partial():
    """Test partial job posting update."""
    update = JobPostingUpdate(
        status="APPLIED",
        notes="Submitted application today",
    )
    
    assert update.status == "APPLIED"
    assert update.notes == "Submitted application today"
    assert update.interest_level is None


@pytest.mark.unit
def test_job_posting_update_status():
    """Test updating job posting status."""
    update = JobPostingUpdate(status="INTERVIEWING")
    assert update.status == "INTERVIEWING"


@pytest.mark.unit
def test_job_posting_response():
    """Test job posting response schema."""
    job = JobPostingResponse(
        id=uuid4(),
        user_id=uuid4(),
        company_name="TechCorp",
        job_title="Engineer",
        job_url="https://example.com/job",
        status="SAVED",
        source="MANUAL",
    )
    
    assert job.company_name == "TechCorp"
    assert job.status == "SAVED"


@pytest.mark.unit
def test_application_create_valid():
    """Test creating valid application."""
    app = ApplicationCreate(
        job_posting_id=uuid4(),
        resume_version_id=uuid4(),
        cover_letter_content="Dear Hiring Manager...",
        demographics_data={"gender": "Prefer not to say"},
    )
    
    assert isinstance(app.job_posting_id, type(uuid4()))
    assert isinstance(app.resume_version_id, type(uuid4()))
    assert "Dear Hiring Manager" in app.cover_letter_content


@pytest.mark.unit
def test_application_missing_required():
    """Test application fails without required IDs."""
    with pytest.raises(ValidationError):
        ApplicationCreate(cover_letter_content="Dear...")


@pytest.mark.unit
def test_application_update_status():
    """Test updating application status."""
    update = ApplicationUpdate(
        status="SUBMITTED",
        submission_method="extension",
    )
    
    assert update.status == "SUBMITTED"
    assert update.submission_method == "extension"


@pytest.mark.unit
def test_application_response():
    """Test application response schema."""
    app = ApplicationResponse(
        id=uuid4(),
        user_id=uuid4(),
        job_posting_id=uuid4(),
        resume_version_id=uuid4(),
        status="DRAFT",
    )
    
    assert app.status == "DRAFT"
    assert isinstance(app.id, type(uuid4()))


@pytest.mark.unit
def test_job_posting_with_optional_fields():
    """Test job posting with all optional fields."""
    job = JobPostingCreate(
        company_name="TechCorp",
        job_title="Engineer",
        job_url="https://example.com",
        location="Remote",
        salary_range="$120k-$180k",
        employment_type="Full-time",
        remote_policy="Remote",
        job_description="Description...",
        requirements="Requirements...",
        nice_to_have="Nice to have...",
        interest_level=4,
        notes="Great opportunity",
    )
    
    assert job.salary_range == "$120k-$180k"
    assert job.remote_policy == "Remote"
    assert job.notes == "Great opportunity"
