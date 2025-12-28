"""Job schemas for API request/response models."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import Field, field_validator, HttpUrl

from app.models.job import ApplicationStatus, JobSource, JobStatus
from app.schemas.base import BaseResponse, BaseSchema


# ============================================================================
# Job Posting
# ============================================================================


class JobPostingBase(BaseSchema):
    """Base job posting schema."""

    company_name: str = Field(..., min_length=1, max_length=255)
    job_title: str = Field(..., min_length=1, max_length=255)
    job_url: HttpUrl
    source: JobSource = JobSource.MANUAL
    location: Optional[str] = Field(None, max_length=255)
    salary_range: Optional[str] = Field(None, max_length=100)
    employment_type: Optional[str] = Field(None, max_length=50)
    remote_policy: Optional[str] = Field(None, max_length=50)
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

    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    job_title: Optional[str] = Field(None, min_length=1, max_length=255)
    job_url: Optional[HttpUrl] = None
    location: Optional[str] = Field(None, max_length=255)
    salary_range: Optional[str] = Field(None, max_length=100)
    employment_type: Optional[str] = Field(None, max_length=50)
    remote_policy: Optional[str] = Field(None, max_length=50)
    job_description: Optional[str] = None
    requirements: Optional[str] = None
    nice_to_have: Optional[str] = None
    interest_level: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class JobStatusUpdate(BaseSchema):
    """Schema for updating job status."""

    status: JobStatus


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
    last_follow_up_date: Optional[date] = None
    next_follow_up_date: Optional[date] = None
    follow_up_notes: Optional[str] = None


class ApplicationResponse(ApplicationBase, BaseResponse):
    """Schema for application API responses."""

    user_id: UUID
    job_posting_id: UUID
    resume_version_id: UUID
    submitted_at: Optional[datetime] = None
    status: ApplicationStatus
    status_updated_at: datetime
    last_follow_up_date: Optional[date] = None
    next_follow_up_date: Optional[date] = None


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


# ============================================================================
# Pagination & List Responses
# ============================================================================


class JobPostingListResponse(BaseSchema):
    """Schema for paginated job postings list."""

    items: list[JobPostingResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ApplicationListResponse(BaseSchema):
    """Schema for paginated applications list."""

    items: list[ApplicationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CoverLetterListResponse(BaseSchema):
    """Schema for cover letters list."""

    items: list[CoverLetterResponse]
    total: int


# ============================================================================
# Search & Filters
# ============================================================================


class JobSearchParams(BaseSchema):
    """Schema for job search parameters."""

    query: Optional[str] = Field(None, description="Search query for full-text search")
    company: Optional[str] = Field(None, description="Filter by company name")
    status: Optional[JobStatus] = Field(None, description="Filter by job status")
    interest_level: Optional[int] = Field(None, ge=1, le=5, description="Filter by interest level")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", description="Sort order (asc/desc)")

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v: str) -> str:
        """Validate sort order."""
        if v not in ("asc", "desc"):
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v: str) -> str:
        """Validate sort field."""
        allowed_fields = {"created_at", "updated_at", "interest_level", "company_name", "job_title"}
        if v not in allowed_fields:
            raise ValueError(f"sort_by must be one of: {', '.join(allowed_fields)}")
        return v


# ============================================================================
# Statistics
# ============================================================================


class JobStatsResponse(BaseSchema):
    """Schema for job statistics."""

    total_jobs: int
    by_status: dict[str, int]
    avg_interest_level: Optional[float] = None
    total_with_applications: int
    recent_jobs_count: int  # Last 30 days


class ApplicationStatsResponse(BaseSchema):
    """Schema for application statistics."""

    total_applications: int
    by_status: dict[str, int]
    response_rate: float  # Percentage
    avg_response_time_days: Optional[float] = None
    applications_this_week: int
    applications_this_month: int


# ============================================================================
# Status Updates
# ============================================================================


class ApplicationStatusUpdate(BaseSchema):
    """Schema for updating application status."""

    status: ApplicationStatus
