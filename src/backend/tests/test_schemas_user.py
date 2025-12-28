"""Tests for user schemas."""

import pytest
from datetime import datetime
from uuid import uuid4

from pydantic import ValidationError

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
)


@pytest.mark.unit
def test_user_create_valid():
    """Test creating valid user schema."""
    data = {
        "email": "test@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test User",
    }
    user = UserCreate(**data)
    
    assert user.email == "test@example.com"
    assert user.password == "SecurePassword123!"
    assert user.full_name == "Test User"


@pytest.mark.unit
def test_user_create_missing_required_fields():
    """Test user creation fails without required fields."""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(email="test@example.com")
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("password",) for error in errors)


@pytest.mark.unit
def test_user_create_invalid_email():
    """Test user creation fails with invalid email."""
    with pytest.raises(ValidationError):
        UserCreate(
            email="invalid-email",
            password="SecurePassword123!",
        )


@pytest.mark.unit
def test_user_create_optional_fields():
    """Test user creation with optional fields."""
    user = UserCreate(
        email="test@example.com",
        password="SecurePassword123!",
        full_name="Test User",
        phone="+1234567890",
        location="San Francisco, CA",
        linkedin_url="https://linkedin.com/in/testuser",
    )
    
    assert user.phone == "+1234567890"
    assert user.location == "San Francisco, CA"
    assert user.linkedin_url == "https://linkedin.com/in/testuser"


@pytest.mark.unit
def test_user_update_partial():
    """Test partial user update."""
    update = UserUpdate(full_name="Updated Name")
    
    assert update.full_name == "Updated Name"
    assert update.email is None
    assert update.phone is None


@pytest.mark.unit
def test_user_update_all_fields():
    """Test updating all fields."""
    update = UserUpdate(
        full_name="Updated Name",
        phone="+9876543210",
        location="New York, NY",
        linkedin_url="https://linkedin.com/in/updated",
        github_url="https://github.com/updated",
        portfolio_url="https://portfolio.example.com",
    )
    
    assert update.full_name == "Updated Name"
    assert update.phone == "+9876543210"
    assert update.location == "New York, NY"


@pytest.mark.unit
def test_user_response_from_model():
    """Test user response schema."""
    user_data = {
        "id": uuid4(),
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True,
        "email_verified": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    
    user = UserResponse(**user_data)
    
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.is_active is True
    assert user.email_verified is False
    # Password hash should not be in response
    assert not hasattr(user, "password_hash")


@pytest.mark.unit
def test_user_login_valid():
    """Test user login schema."""
    login = UserLogin(
        email="test@example.com",
        password="SecurePassword123!",
    )
    
    assert login.email == "test@example.com"
    assert login.password == "SecurePassword123!"


@pytest.mark.unit
def test_user_login_missing_password():
    """Test login fails without password."""
    with pytest.raises(ValidationError):
        UserLogin(email="test@example.com")


@pytest.mark.unit
def test_user_response_serialization():
    """Test user response can be serialized to dict."""
    user = UserResponse(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        is_active=True,
        email_verified=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    user_dict = user.model_dump()
    
    assert "id" in user_dict
    assert "email" in user_dict
    assert "full_name" in user_dict
    assert "password_hash" not in user_dict
