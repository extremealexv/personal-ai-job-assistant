"""Base Pydantic schemas with common fields."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common Pydantic configuration."""

    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode for SQLAlchemy models
        populate_by_name=True,  # Allow population by field name or alias
        str_strip_whitespace=True,  # Strip whitespace from strings
        validate_assignment=True,  # Validate on assignment
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""

    created_at: datetime
    updated_at: datetime


class IDSchema(BaseSchema):
    """Schema with ID field."""

    id: UUID


class BaseResponse(IDSchema, TimestampSchema):
    """Base response schema with ID and timestamps."""

    pass
