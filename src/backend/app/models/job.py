"""Job and application-related models."""

import enum
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.resume import ResumeVersion
    from app.models.prompt import PromptTemplate
    from app.models.email import EmailThread
    from app.models.analytics import InterviewEvent


class JobStatus(str, enum.Enum):
    """Job posting lifecycle status."""

    SAVED = "saved"
    PREPARED = "prepared"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    REJECTED = "rejected"
    OFFER = "offer"
    CLOSED = "closed"


class JobSource(str, enum.Enum):
    """Source of job posting."""

    MANUAL = "manual"
    EXTENSION = "extension"
    API = "api"


class ApplicationStatus(str, enum.Enum):
    """Application submission status."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    VIEWED = "viewed"
    PHONE_SCREEN = "phone_screen"
    TECHNICAL = "technical"
    ONSITE = "onsite"
    OFFER = "offer"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class JobPosting(Base):
    """Job posting saved for application."""

    __tablename__ = "job_postings"

    # Foreign keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Basic information
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    job_url: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[JobSource] = mapped_column(
        Enum(JobSource, name="job_source"), default=JobSource.MANUAL, nullable=False
    )

    # Job details
    location: Mapped[Optional[str]] = mapped_column(String(255))
    salary_range: Mapped[Optional[str]] = mapped_column(String(100))
    employment_type: Mapped[Optional[str]] = mapped_column(String(50))
    remote_policy: Mapped[Optional[str]] = mapped_column(String(50))

    # Description (full-text searchable)
    job_description: Mapped[Optional[str]] = mapped_column(Text)
    requirements: Mapped[Optional[str]] = mapped_column(Text)
    nice_to_have: Mapped[Optional[str]] = mapped_column(Text)

    # ATS detection
    ats_platform: Mapped[Optional[str]] = mapped_column(String(100))
    ats_detected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Status tracking
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status"), default=JobStatus.SAVED, nullable=False
    )
    status_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )

    # Keywords (extracted for matching)
    extracted_keywords: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))

    # Priority/interest
    interest_level: Mapped[Optional[int]] = mapped_column(Integer)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="job_postings")
    resume_versions: Mapped[list["ResumeVersion"]] = relationship(
        back_populates="job_posting"
    )
    applications: Mapped[list["Application"]] = relationship(
        back_populates="job_posting", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<JobPosting(company={self.company_name}, title={self.job_title})>"


class Application(Base):
    """Application submission record."""

    __tablename__ = "applications"

    # Foreign keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    job_posting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_postings.id", ondelete="CASCADE"),
        nullable=False,
    )
    resume_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resume_versions.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Submission details
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    submission_method: Mapped[Optional[str]] = mapped_column(String(50))

    # Status tracking
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status"),
        default=ApplicationStatus.DRAFT,
        nullable=False,
    )
    status_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )

    # Demographics (if collected, stored encrypted or as IDs)
    demographics_data: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Follow-up tracking
    last_follow_up_date: Mapped[Optional[date]] = mapped_column(Date)
    next_follow_up_date: Mapped[Optional[date]] = mapped_column(Date)
    follow_up_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="applications")
    job_posting: Mapped["JobPosting"] = relationship(back_populates="applications")
    resume_version: Mapped["ResumeVersion"] = relationship(back_populates="applications")
    cover_letters: Mapped[list["CoverLetter"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
    email_threads: Mapped[list["EmailThread"]] = relationship(
        back_populates="application"
    )
    interview_events: Mapped[list["InterviewEvent"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Application(job={self.job_posting_id}, status={self.status})>"


class CoverLetter(Base):
    """Generated cover letter for application."""

    __tablename__ = "cover_letters"

    # Foreign keys
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # AI generation metadata
    prompt_template_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("prompt_templates.id", ondelete="SET NULL")
    )
    ai_model_used: Mapped[Optional[str]] = mapped_column(String(100))
    generation_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Versioning
    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Generated files
    pdf_file_path: Mapped[Optional[str]] = mapped_column(String(1000))

    # Relationships
    application: Mapped["Application"] = relationship(back_populates="cover_letters")
    prompt_template: Mapped[Optional["PromptTemplate"]] = relationship(
        back_populates="cover_letters"
    )

    def __repr__(self) -> str:
        return f"<CoverLetter(application={self.application_id}, version={self.version_number})>"
