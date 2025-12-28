"""Prompt template models."""

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.resume import ResumeVersion
    from app.models.job import CoverLetter


class PromptTask(str, enum.Enum):
    """Task type for prompt template."""

    RESUME_TAILOR = "resume_tailor"
    COVER_LETTER = "cover_letter"
    FORM_ANSWERS = "form_answers"
    EMAIL_CLASSIFICATION = "email_classification"


class PromptTemplate(Base):
    """Versioned AI prompt templates."""

    __tablename__ = "prompt_templates"

    # Foreign keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Template metadata
    task_type: Mapped[PromptTask] = mapped_column(
        Enum(PromptTask, name="prompt_task"), nullable=False
    )
    role_type: Mapped[Optional[str]] = mapped_column(String(100))

    # Template content
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)

    # System vs user prompt
    is_system_prompt: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    parent_template_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("prompt_templates.id", ondelete="SET NULL")
    )

    # Usage statistics
    times_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_satisfaction_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="prompt_templates")
    parent_template: Mapped[Optional["PromptTemplate"]] = relationship(
        remote_side="PromptTemplate.id", foreign_keys=[parent_template_id]
    )
    resume_versions: Mapped[list["ResumeVersion"]] = relationship(
        back_populates="prompt_template"
    )
    cover_letters: Mapped[list["CoverLetter"]] = relationship(
        back_populates="prompt_template"
    )

    def __repr__(self) -> str:
        return f"<PromptTemplate(name={self.name}, task={self.task_type}, active={self.is_active})>"
