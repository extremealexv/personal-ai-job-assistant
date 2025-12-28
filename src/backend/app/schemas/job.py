"""Job schemas for API request/response models."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import Field

from app.models.job import ApplicationStatus, JobSource, JobStatus
from app.schemas.base import BaseResponse, BaseSchema


# ============================================================================
# Job Posting
# ============================================================================


class JobPostingBase(BaseSchema):
    """Base job posting schema."""

    company_name: str
    job_title: str
    job_url: str
    source: JobSource = JobSource.MANUAL
    location: Optional[str] = None
    salary_range: Optional[str] = None
    employment_type: Optional[str] = None
    remote_policy: Optional[str] = None
    job_description: Optional[str] = None
    requirements: Optional[str] = None
    nice_to_have: Optional[str] = None
    interest_level: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class JobPostingCreate(JobPostingBase):
    """Schema for creating a job posting."""

    pass


class JobPostingUpdate(BaseSchema):
    """Schema for updating a job posting."""

    company_name: Optional[str] = None
    job_title: Optional[str] = None
    job_url: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    employment_type: Optional[str] = None
    remote_policy: Optional[str] = None
    job_description: Optional[str] = None
    requirements: Optional[str] = None
    nice_to_have: Optional[str] = None
    status: Optional[JobStatus] = None
    interest_level: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class JobPostingResponse(JobPostingBase, BaseResponse):
    """Schema for job posting API responses."""

    user_id: UUID
    status: JobStatus
    status_updated_at: datetime
    ats_platform: Optional[str] = None
    ats_detected_at: Optional[datetime] = None
    extracted_keywords: list[str] = Field(default_factory=list)


# ============================================================================
# Application
# ============================================================================


class ApplicationBase(BaseSchema):
    """Base application schema."""

    submission_method: Optional[str] = None
    demographics_data: Optional[dict[str, Any]] = Field(default_factory=dict)
    follow_up_notes: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    """Schema for creating an application."""

    job_posting_id: UUID
    resume_version_id: UUID


class ApplicationUpdate(BaseSchema):
    """Schema for updating an application."""

    status: Optional[ApplicationStatus] = None
    submission_method: Optional[str] = None
    demographics_data: Optional[dict[str, Any]] = None
    last_follow_up_date: Optional[datetime] = None
    next_follow_up_date: Optional[datetime] = None
    follow_up_notes: Optional[str] = None


class ApplicationResponse(ApplicationBase, BaseResponse):
    """Schema for application API responses."""

    user_id: UUID
    job_posting_id: UUID
    resume_version_id: UUID
    submitted_at: Optional[datetime] = None
    status: ApplicationStatus
    status_updated_at: datetime
    last_follow_up_date: Optional[datetime] = None
    next_follow_up_date: Optional[datetime] = None


# ============================================================================
# Cover Letter
# ============================================================================


class CoverLetterBase(BaseSchema):
    """Base cover letter schema."""

    content: str


class CoverLetterCreate(CoverLetterBase):
    """Schema for creating a cover letter."""

    application_id: UUID
    prompt_template_id: Optional[UUID] = None
    ai_model_used: Optional[str] = None


class CoverLetterUpdate(BaseSchema):
    """Schema for updating a cover letter."""

    content: Optional[str] = None
    is_active: Optional[bool] = None
    pdf_file_path: Optional[str] = None


class CoverLetterResponse(CoverLetterBase, BaseResponse):
    """Schema for cover letter API responses."""

    application_id: UUID
    prompt_template_id: Optional[UUID] = None
    ai_model_used: Optional[str] = None
    generation_timestamp: Optional[datetime] = None
    version_number: int
    is_active: bool
    pdf_file_path: Optional[str] = None
