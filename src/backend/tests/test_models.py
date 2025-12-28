"""Tests for database models."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.integration
async def test_create_user(db_session: AsyncSession):
    """Test creating a user in the database."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        full_name="Test User",
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.is_active is True
    assert user.email_verified is False
    assert user.created_at is not None
    assert user.updated_at is not None


@pytest.mark.integration
async def test_user_unique_email(db_session: AsyncSession):
    """Test that user email must be unique."""
    from sqlalchemy.exc import IntegrityError
    
    # Create first user
    user1 = User(
        email="test@example.com",
        password_hash="hashed_password",
        full_name="User One",
    )
    db_session.add(user1)
    await db_session.commit()
    
    # Try to create second user with same email
    user2 = User(
        email="test@example.com",
        password_hash="hashed_password",
        full_name="User Two",
    )
    db_session.add(user2)
    
    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.integration
async def test_user_to_dict(db_session: AsyncSession):
    """Test User.to_dict() method."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        full_name="Test User",
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    user_dict = user.to_dict()
    
    assert "id" in user_dict
    assert "email" in user_dict
    assert "full_name" in user_dict
    assert "created_at" in user_dict
    assert "updated_at" in user_dict
    assert user_dict["email"] == "test@example.com"
    # Password hash should not be in dict
    assert "password_hash" not in user_dict or user_dict.get("password_hash") is None
