"""Analytics schemas for API request/response models."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.models.analytics import InterviewType
from app.schemas.base import BaseResponse, BaseSchema


# ============================================================================
# Interview Event
# ============================================================================


class InterviewEventBase(BaseSchema):
    """Base interview event schema."""

    interview_type: InterviewType
    scheduled_at: datetime
    duration_minutes: int = 60
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    interviewer_names: list[str] = Field(default_factory=list)
    interviewer_emails: list[str] = Field(default_factory=list)
    preparation_notes: Optional[str] = None


class InterviewEventCreate(InterviewEventBase):
    """Schema for creating an interview event."""

    application_id: UUID


class InterviewEventUpdate(BaseSchema):
    """Schema for updating an interview event."""

    interview_type: Optional[InterviewType] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    interviewer_names: Optional[list[str]] = None
    interviewer_emails: Optional[list[str]] = None
    preparation_notes: Optional[str] = None
    post_interview_notes: Optional[str] = None
    feedback_rating: Optional[int] = Field(None, ge=1, le=5)
    completed: Optional[bool] = None
    google_calendar_event_id: Optional[str] = None
    synced_to_calendar: Optional[bool] = None


class InterviewEventResponse(InterviewEventBase, BaseResponse):
    """Schema for interview event API responses."""

    application_id: UUID
    google_calendar_event_id: Optional[str] = None
    synced_to_calendar: bool
    post_interview_notes: Optional[str] = None
    feedback_rating: Optional[int] = Field(None, ge=1, le=5)
    completed: bool
    completed_at: Optional[datetime] = None


# ============================================================================
# Analytics Snapshot
# ============================================================================


class AnalyticsSnapshotBase(BaseSchema):
    """Base analytics snapshot schema."""

    snapshot_date: date
    total_applications: int = 0
    applications_this_week: int = 0
    applications_this_month: int = 0
    total_responses: int = 0
    response_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    total_interviews: int = 0
    interview_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    total_offers: int = 0
    offer_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    avg_response_time_days: Optional[Decimal] = Field(None, ge=0)
    avg_time_to_interview_days: Optional[Decimal] = Field(None, ge=0)


class AnalyticsSnapshotCreate(AnalyticsSnapshotBase):
    """Schema for creating an analytics snapshot."""

    pass


class AnalyticsSnapshotUpdate(BaseSchema):
    """Schema for updating an analytics snapshot."""

    total_applications: Optional[int] = None
    applications_this_week: Optional[int] = None
    applications_this_month: Optional[int] = None
    total_responses: Optional[int] = None
    response_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    total_interviews: Optional[int] = None
    interview_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    total_offers: Optional[int] = None
    offer_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    avg_response_time_days: Optional[Decimal] = Field(None, ge=0)
    avg_time_to_interview_days: Optional[Decimal] = Field(None, ge=0)


class AnalyticsSnapshotResponse(AnalyticsSnapshotBase, BaseResponse):
    """Schema for analytics snapshot API responses."""

    user_id: UUID
