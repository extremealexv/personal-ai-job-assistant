"""Email thread schemas for API request/response models."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.models.email import EmailClassification
from app.schemas.base import BaseResponse, BaseSchema


class EmailThreadBase(BaseSchema):
    """Base email thread schema."""

    gmail_message_id: str
    gmail_thread_id: str
    subject: Optional[str] = None
    sender_email: Optional[str] = None
    sender_name: Optional[str] = None
    received_at: datetime
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    has_attachments: bool = False
    attachment_names: list[str] = Field(default_factory=list)


class EmailThreadCreate(EmailThreadBase):
    """Schema for creating an email thread."""

    application_id: Optional[UUID] = None


class EmailThreadResponse(EmailThreadBase, BaseResponse):
    """Schema for email thread API responses."""

    user_id: UUID
    application_id: Optional[UUID] = None
    classification: Optional[EmailClassification] = None
    classification_confidence: Optional[Decimal] = Field(None, ge=0, le=1)
    classified_at: Optional[datetime] = None
