"""Pydantic schemas for cover letter validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field, validator

from app.schemas.base import BaseSchema


class CoverLetterBase(BaseSchema):
    """Base schema for cover letters."""

    content: str = Field(
        ..., min_length=100, max_length=10000, description="Cover letter content"
    )


class CoverLetterCreate(CoverLetterBase):
    """Schema for creating a new cover letter."""

    application_id: UUID = Field(..., description="Associated application ID")
    prompt_template_id: Optional[UUID] = Field(
        None, description="Prompt template used for AI generation"
    )
    ai_model_used: Optional[str] = Field(
        None, max_length=100, description="AI model used for generation"
    )


class CoverLetterUpdate(BaseSchema):
    """Schema for updating an existing cover letter."""

    content: Optional[str] = Field(
        None, min_length=100, max_length=10000, description="Updated cover letter content"
    )
    is_active: Optional[bool] = Field(None, description="Whether this version is active")


class CoverLetterResponse(CoverLetterBase):
    """Schema for cover letter response."""

    id: UUID
    application_id: UUID
    prompt_template_id: Optional[UUID]
    ai_model_used: Optional[str]
    version_number: int
    is_active: bool
    generation_timestamp: Optional[datetime]
    pdf_file_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class CoverLetterListResponse(BaseSchema):
    """Schema for paginated cover letter list."""

    items: list[CoverLetterResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CoverLetterVersionsResponse(BaseSchema):
    """Schema for all versions of a cover letter."""

    application_id: UUID
    versions: list[CoverLetterResponse]
    active_version: Optional[CoverLetterResponse]


class CoverLetterGenerateRequest(BaseSchema):
    """Schema for AI-generated cover letter request."""

    application_id: UUID = Field(..., description="Application to generate cover letter for")
    prompt_template_id: Optional[UUID] = Field(
        None, description="Optional custom prompt template"
    )
    tone: Optional[str] = Field(
        "professional", description="Tone of the cover letter (professional, enthusiastic, formal)"
    )
    emphasis_points: Optional[list[str]] = Field(
        None, description="Key points to emphasize in the cover letter"
    )

    @validator("tone")
    def validate_tone(cls, v: Optional[str]) -> Optional[str]:
        """Validate tone value."""
        if v is None:
            return v
        
        allowed_tones = ["professional", "enthusiastic", "formal", "creative"]
        if v.lower() not in allowed_tones:
            raise ValueError(
                f"Tone must be one of: {', '.join(allowed_tones)}"
            )
        return v.lower()


class CoverLetterSearchParams(BaseSchema):
    """Search parameters for cover letters."""

    application_id: Optional[UUID] = Field(None, description="Filter by application")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    ai_model_used: Optional[str] = Field(None, description="Filter by AI model")
    
    # Pagination
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    
    # Sorting
    sort_by: str = Field("created_at", description="Field to sort by")
    sort_order: str = Field("desc", description="Sort order (asc or desc)")

    @validator("sort_by")
    def validate_sort_by(cls, v: str) -> str:
        """Validate sort_by field."""
        allowed_fields = [
            "created_at",
            "updated_at",
            "version_number",
            "is_active",
        ]
        if v not in allowed_fields:
            raise ValueError(f"sort_by must be one of: {', '.join(allowed_fields)}")
        return v

    @validator("sort_order")
    def validate_sort_order(cls, v: str) -> str:
        """Validate sort order."""
        if v.lower() not in ["asc", "desc"]:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v.lower()
