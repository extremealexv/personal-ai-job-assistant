"""Pydantic schemas for authentication endpoints."""
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.security import is_valid_password, get_password_strength_message


class UserRegister(BaseModel):
    """Schema for user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    full_name: str = Field(..., min_length=1, max_length=255, description="User full name")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets strength requirements."""
        if not is_valid_password(v):
            raise ValueError(get_password_strength_message())
        return v


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str = Field(..., description="JWT refresh token")


class PasswordChange(BaseModel):
    """Schema for password change."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate new password meets strength requirements."""
        if not is_valid_password(v):
            raise ValueError(get_password_strength_message())
        return v


class LogoutRequest(BaseModel):
    """Schema for logout request."""

    refresh_token: str = Field(..., description="JWT refresh token to invalidate")
