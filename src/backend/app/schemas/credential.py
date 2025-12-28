"""Credential schemas for API request/response models."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseResponse, BaseSchema


class CredentialBase(BaseSchema):
    """Base credential schema."""

    platform: str
    username: Optional[str] = None
    additional_data: Optional[dict[str, Any]] = Field(default_factory=dict)


class CredentialCreate(CredentialBase):
    """Schema for creating a credential.
    
    Password is provided in plaintext and will be encrypted before storage.
    """

    password: str = Field(..., min_length=1)


class CredentialUpdate(BaseSchema):
    """Schema for updating a credential."""

    username: Optional[str] = None
    password: Optional[str] = Field(None, min_length=1)
    additional_data: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None


class CredentialResponse(CredentialBase, BaseResponse):
    """Schema for credential API responses.
    
    Password is never included in responses.
    """

    user_id: UUID
    last_used: Optional[datetime] = None
    is_active: bool
