"""User model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.resume import MasterResume
    from app.models.job import JobPosting, Application
    from app.models.prompt import PromptTemplate
    from app.models.credential import Credential
    from app.models.analytics import AnalyticsSnapshot


class User(Base):
    """User model for authentication and profile.
    
    Single-user system, but designed to support potential multi-user expansion.
    """

    __tablename__ = "users"

    # Authentication
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile information
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500))
    github_url: Mapped[Optional[str]] = mapped_column(String(500))
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Account status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    failed_login_attempts: Mapped[int] = mapped_column(default=0, nullable=False)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # WebAuthn credentials (optional 2FA)
    webauthn_credentials: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    master_resumes: Mapped[list["MasterResume"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    job_postings: Mapped[list["JobPosting"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    applications: Mapped[list["Application"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    prompt_templates: Mapped[list["PromptTemplate"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    credentials: Mapped[list["Credential"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    analytics_snapshots: Mapped[list["AnalyticsSnapshot"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(email={self.email}, active={self.is_active})>"
