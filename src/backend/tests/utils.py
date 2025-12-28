"""Test utilities and helper functions."""

from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def create_test_user(
    db: AsyncSession,
    email: str = "test@example.com",
    full_name: str = "Test User",
    **kwargs: Any,
) -> User:
    """Create a test user with default values.
    
    Args:
        db: Database session
        email: User email
        full_name: User full name
        **kwargs: Additional user fields
        
    Returns:
        Created user instance
    """
    user = User(
        email=email,
        password_hash="hashed_password",  # TODO: Use proper hashing
        full_name=full_name,
        is_active=kwargs.get("is_active", True),
        email_verified=kwargs.get("email_verified", True),
        **kwargs,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """Get user by ID.
    
    Args:
        db: Database session
        user_id: User UUID
        
    Returns:
        User instance or None
    """
    from sqlalchemy import select
    
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email.
    
    Args:
        db: Database session
        email: User email
        
    Returns:
        User instance or None
    """
    from sqlalchemy import select
    
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


def assert_valid_uuid(value: Any) -> None:
    """Assert that value is a valid UUID.
    
    Args:
        value: Value to check
        
    Raises:
        AssertionError: If value is not a valid UUID
    """
    try:
        UUID(str(value))
    except (ValueError, AttributeError):
        raise AssertionError(f"'{value}' is not a valid UUID")


def assert_dict_contains(actual: dict, expected: dict) -> None:
    """Assert that actual dict contains all key-value pairs from expected dict.
    
    Args:
        actual: Actual dictionary
        expected: Expected key-value pairs
        
    Raises:
        AssertionError: If expected keys/values not in actual
    """
    for key, value in expected.items():
        assert key in actual, f"Key '{key}' not found in actual dict"
        assert actual[key] == value, f"Expected {key}={value}, got {actual[key]}"
