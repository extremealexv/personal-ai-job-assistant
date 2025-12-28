"""User schemas for API request/response models."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field

from app.schemas.base import BaseResponse, BaseSchema


class UserBase(BaseSchema):
    """Base user schema with common fields."""

    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class UserUpdate(BaseSchema):
    """Schema for updating a user."""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase, BaseResponse):
    """Schema for user API responses."""

    is_active: bool
    email_verified: bool
    last_login: Optional[datetime] = None
    failed_login_attempts: int


class UserLogin(BaseSchema):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserToken(BaseSchema):
    """Schema for authentication token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: UUID
