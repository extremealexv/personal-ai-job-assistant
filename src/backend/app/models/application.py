from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, String, DateTime, Enum as PgEnum, ForeignKey, Integer, JSON, Boolean
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base

class ApplicationStatus(str, Enum):
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

class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    job_posting_id = Column(UUID(as_uuid=True), ForeignKey("job_postings.id"), nullable=False)
    resume_version_id = Column(UUID(as_uuid=True), nullable=False)

    submitted_at = Column(DateTime)
    submission_method = Column(String(50))
    status = Column(PgEnum(ApplicationStatus), default=ApplicationStatus.DRAFT, nullable=False)
    status_updated_at = Column(DateTime, default=datetime.utcnow)
    demographics_data = Column(JSON)
    last_follow_up_date = Column(DateTime)
    next_follow_up_date = Column(DateTime)
    follow_up_notes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    job_posting = relationship("JobPosting", back_populates="applications")
    cover_letters = relationship("CoverLetter", back_populates="application")
