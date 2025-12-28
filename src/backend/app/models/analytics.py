"""Analytics and interview event models."""

import enum
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.job import Application


class InterviewType(str, enum.Enum):
    """Type of interview."""

    PHONE_SCREEN = "phone_screen"
    TECHNICAL_SCREEN = "technical_screen"
    CODING_CHALLENGE = "coding_challenge"
    ONSITE = "onsite"
    BEHAVIORAL = "behavioral"
    FINAL_ROUND = "final_round"
    OTHER = "other"


class InterviewEvent(Base):
    """Interview scheduling and tracking."""

    __tablename__ = "interview_events"

    # Foreign keys
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Interview details
    interview_type: Mapped[InterviewType] = mapped_column(
        Enum(InterviewType, name="interview_type"), nullable=False
    )
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)

    # Location/meeting info
    location: Mapped[Optional[str]] = mapped_column(String(500))
    meeting_link: Mapped[Optional[str]] = mapped_column(String(500))

    # Interviewers
    interviewer_names: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))
    interviewer_emails: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))

    # Google Calendar integration
    google_calendar_event_id: Mapped[Optional[str]] = mapped_column(String(255))
    synced_to_calendar: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Notes & feedback
    preparation_notes: Mapped[Optional[str]] = mapped_column(Text)
    post_interview_notes: Mapped[Optional[str]] = mapped_column(Text)
    feedback_rating: Mapped[Optional[int]] = mapped_column(Integer)

    # Status
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    application: Mapped["Application"] = relationship(back_populates="interview_events")

    def __repr__(self) -> str:
        return f"<InterviewEvent(type={self.interview_type}, scheduled={self.scheduled_at})>"


class AnalyticsSnapshot(Base):
    """Daily aggregated metrics for performance tracking."""

    __tablename__ = "analytics_snapshots"

    # Foreign keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Application metrics
    total_applications: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    applications_this_week: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    applications_this_month: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Response metrics
    total_responses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    response_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))

    # Interview metrics
    total_interviews: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    interview_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))

    # Offer metrics
    total_offers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    offer_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))

    # Time metrics
    avg_response_time_days: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1))
    avg_time_to_interview_days: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="analytics_snapshots")

    def __repr__(self) -> str:
        return f"<AnalyticsSnapshot(date={self.snapshot_date}, apps={self.total_applications})>"
