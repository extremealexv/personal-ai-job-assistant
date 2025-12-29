from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, ForeignKey, Integer, Boolean
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base

class CoverLetter(Base):
    __tablename__ = "cover_letters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False)
    content = Column(String, nullable=False)
    prompt_template_id = Column(UUID(as_uuid=True))
    ai_model_used = Column(String(100))
    generation_timestamp = Column(DateTime)
    version_number = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    pdf_file_path = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    application = relationship("Application", back_populates="cover_letters")
