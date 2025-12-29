"""Application schemas for API validation."""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.job import ApplicationStatus


# Base schemas
class ApplicationBase(BaseModel):
    """Base application schema with common fields."""

    submission_method: Optional[str] = Field(None, max_length=50)
    demographics_data: Optional[dict[str, str]] = None
    last_follow_up_date: Optional[date] = None
    next_follow_up_date: Optional[date] = None
    follow_up_notes: Optional[str] = None


# Create schema
class ApplicationCreate(ApplicationBase):
    """Schema for creating a new application."""

    job_posting_id: UUID
    resume_version_id: UUID
    submitted_at: Optional[datetime] = None
    status: Optional[ApplicationStatus] = Field(
        default=ApplicationStatus.DRAFT,
        description="Initial application status"
    )

    @field_validator("status")
    @classmethod
    def validate_initial_status(cls, v: ApplicationStatus) -> ApplicationStatus:
        """Ensure initial status is DRAFT or SUBMITTED."""
        if v not in (ApplicationStatus.DRAFT, ApplicationStatus.SUBMITTED):
            raise ValueError("Initial status must be 'draft' or 'submitted'")
        return v


# Update schema
class ApplicationUpdate(ApplicationBase):
    """Schema for updating an existing application."""

    resume_version_id: Optional[UUID] = None
    submitted_at: Optional[datetime] = None


# Status update schema
class ApplicationStatusUpdate(BaseModel):
    """Schema for updating application status only."""

    status: ApplicationStatus

    @field_validator("status")
    @classmethod
    def validate_status_transition(cls, v: ApplicationStatus) -> ApplicationStatus:
        """Validate status is a valid application status."""
        if v not in ApplicationStatus:
            raise ValueError(f"Invalid status: {v}")
        return v


# Response schema
class ApplicationResponse(ApplicationBase):
    """Schema for application response."""

    id: UUID
    user_id: UUID
    job_posting_id: UUID
    resume_version_id: UUID
    submitted_at: Optional[datetime]
    status: ApplicationStatus
    status_updated_at: datetime
    created_at: datetime
    updated_at: datetime

    # Nested job posting info (optional, for list views)
    job_company_name: Optional[str] = None
    job_title: Optional[str] = None

    model_config = {"from_attributes": True}


# List response with pagination
class ApplicationListResponse(BaseModel):
    """Paginated list of applications."""

    items: list[ApplicationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Search/filter parameters
class ApplicationSearchParams(BaseModel):
    """Parameters for searching and filtering applications."""

    # Pagination
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    # Filters
    job_posting_id: Optional[UUID] = None
    status: Optional[ApplicationStatus] = None
    submitted_after: Optional[datetime] = None
    submitted_before: Optional[datetime] = None

    # Sorting
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc")

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
        allowed_fields = [
            "created_at",
            "updated_at",
            "submitted_at",
            "status",
            "status_updated_at",
        ]
        if v not in allowed_fields:
            raise ValueError(f"sort_by must be one of: {', '.join(allowed_fields)}")
        return v


# Statistics response
class ApplicationStatsResponse(BaseModel):
    """Application statistics response."""

    total_applications: int
    by_status: dict[str, int]
    submitted_count: int
    draft_count: int
    response_rate: Optional[float] = Field(
        None, description="Percentage of applications with responses"
    )
    avg_days_to_response: Optional[float] = Field(
        None, description="Average days between submission and first response"
    )
    recent_applications_count: int = Field(
        description="Applications in last 30 days"
    )
