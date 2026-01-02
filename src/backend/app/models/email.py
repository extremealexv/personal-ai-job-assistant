"""Email tracking model for Gmail integration."""

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.job import Application


class EmailClassification(str, enum.Enum):
    """Email classification types."""

    CONFIRMATION = "confirmation"
    INTERVIEW = "interview"
    REJECTION = "rejection"
    OFFER = "offer"
    OTHER = "other"


class EmailThread(Base):
    """Email thread for application follow-ups."""

    __tablename__ = "email_threads"

    # Foreign keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    application_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applications.id", ondelete="SET NULL")
    )

    # Gmail metadata
    gmail_message_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    gmail_thread_id: Mapped[Optional[str]] = mapped_column(String(255))

    # Email details
    subject: Mapped[Optional[str]] = mapped_column(String(500))
    sender_email: Mapped[Optional[str]] = mapped_column(String(255))
    sender_name: Mapped[Optional[str]] = mapped_column(String(255))
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Classification (AI-powered)
    classification: Mapped[Optional[EmailClassification]] = mapped_column(
        Enum(EmailClassification, name="email_classification", values_callable=lambda x: [e.value for e in x])
    )
    classification_confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2))
    classified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Body content (stored for searching)
    body_text: Mapped[Optional[str]] = mapped_column(Text)
    body_html: Mapped[Optional[str]] = mapped_column(Text)

    # Attachments
    has_attachments: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    attachment_names: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))

    # Relationships
    user: Mapped["User"] = relationship()
    application: Mapped[Optional["Application"]] = relationship(back_populates="email_threads")

    def __repr__(self) -> str:
        return f"<EmailThread(subject={self.subject}, classification={self.classification})>"
