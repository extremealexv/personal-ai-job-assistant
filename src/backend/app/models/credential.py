"""Credential storage model for encrypted job board credentials."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, LargeBinary, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Credential(Base):
    """Encrypted credentials for job board platforms."""

    __tablename__ = "credentials"

    # Foreign keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Platform information
    platform: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255))

    # Encrypted password (using pgcrypto or application-level encryption)
    password_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    # Additional fields (stored as JSONB for flexibility)
    additional_data: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Usage tracking
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="credentials")

    def __repr__(self) -> str:
        return f"<Credential(platform={self.platform}, username={self.username})>"
