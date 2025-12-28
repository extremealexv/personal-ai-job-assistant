"""Integration tests for authentication endpoints."""

from datetime import datetime, timedelta, timezone
import uuid

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, get_password_hash
from app.models.user import User


# ============================================================================
# Test Data Fixtures
# ============================================================================


@pytest.fixture
async def test_user_data() -> dict:
    """Test user registration data with unique email."""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"testuser-{unique_id}@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User",
    }


@pytest.fixture
async def existing_user(db_session: AsyncSession) -> User:
    """Create an existing user in the database with unique email."""
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        email=f"existing-{unique_id}@example.com",
        password_hash=get_password_hash("ExistingPass123!"),
        full_name="Existing User",
        is_active=True,
        email_verified=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def locked_user(db_session: AsyncSession) -> User:
    """Create a locked user (account locked due to failed attempts) with unique email."""
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        email=f"locked-{unique_id}@example.com",
        password_hash=get_password_hash("LockedPass123!"),
        full_name="Locked User",
        is_active=True,
        failed_login_attempts=5,
        locked_until=datetime.now(timezone.utc) + timedelta(minutes=15),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def inactive_user(db_session: AsyncSession) -> User:
    """Create an inactive user with unique email."""
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        email=f"inactive-{unique_id}@example.com",
        password_hash=get_password_hash("InactivePass123!"),
        full_name="Inactive User",
        is_active=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ============================================================================
# Registration Tests
# ============================================================================


@pytest.mark.integration
class TestRegistration:
    """Test user registration endpoint."""

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_register_new_user_success(
        self, async_client: AsyncClient, test_user_data: dict, db_session: AsyncSession
    ):
        """Test successful user registration."""
        response = await async_client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Check response structure
        assert "id" in data
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
        assert data["is_active"] is True
        assert data["email_verified"] is False
        assert "password" not in data
        assert "password_hash" not in data
        
        # Verify user was created in database
        result = await db_session.execute(
            select(User).where(User.email == test_user_data["email"])
        )
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.email == test_user_data["email"]

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self, async_client: AsyncClient, existing_user: User
    ):
        """Test that registering with duplicate email fails."""
        duplicate_data = {
            "email": existing_user.email,
            "password": "AnotherPass123!",
            "full_name": "Duplicate User",
        }
        
        response = await async_client.post("/api/v1/auth/register", json=duplicate_data)
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_register_weak_password(self, async_client: AsyncClient):
        """Test that weak passwords are rejected."""
        weak_passwords = [
            "short",  # Too short
            "nouppercase1!",  # No uppercase
            "NOLOWERCASE1!",  # No lowercase
            "NoDigits!",  # No digits
            "NoSpecial123",  # No special characters
        ]
        
        for weak_password in weak_passwords:
            user_data = {
                "email": "weakpass@example.com",
                "password": weak_password,
                "full_name": "Weak Password User",
            }
            
            response = await async_client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_register_invalid_email(self, async_client: AsyncClient):
        """Test that invalid email formats are rejected."""
        invalid_emails = [
            "notanemail",
            "@nodomain.com",
            "no@domain",
            "spaces in@email.com",
        ]
        
        for invalid_email in invalid_emails:
            user_data = {
                "email": invalid_email,
                "password": "ValidPass123!",
                "full_name": "Invalid Email User",
            }
            
            response = await async_client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_register_missing_required_fields(self, async_client: AsyncClient):
        """Test that missing required fields are rejected."""
        # Missing email
        response = await async_client.post(
            "/api/v1/auth/register",
            json={"password": "ValidPass123!", "full_name": "User"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Missing password
        response = await async_client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "full_name": "User"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_register_password_is_hashed(
        self, async_client: AsyncClient, test_user_data: dict, db_session: AsyncSession
    ):
        """Test that passwords are hashed in the database."""
        response = await async_client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Retrieve user from database
        result = await db_session.execute(
            select(User).where(User.email == test_user_data["email"])
        )
        user = result.scalar_one()
        
        # Password hash should not match plain password
        assert user.password_hash != test_user_data["password"]
        # Password hash should be bcrypt format
        assert user.password_hash.startswith("$2b$")


# ============================================================================
# Login Tests
# ============================================================================


@pytest.mark.integration
class TestLogin:
    """Test user login endpoint."""

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_login_success(self, async_client: AsyncClient, existing_user: User):
        """Test successful login."""
        login_data = {
            "email": existing_user.email,
            "password": "ExistingPass123!",
        }
        
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check token response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0
        
        # Tokens should be non-empty strings
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
        assert isinstance(data["refresh_token"], str)
        assert len(data["refresh_token"]) > 0

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_login_incorrect_password(
        self, async_client: AsyncClient, existing_user: User
    ):
        """Test login with incorrect password."""
        login_data = {
            "email": existing_user.email,
            "password": "WrongPassword123!",
        }
        
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        """Test login with non-existent email."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!",
        }
        
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_login_inactive_user(
        self, async_client: AsyncClient, inactive_user: User
    ):
        """Test that inactive users cannot login."""
        login_data = {
            "email": inactive_user.email,
            "password": "InactivePass123!",
        }
        
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "inactive" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_locked_account(
        self, async_client: AsyncClient, locked_user: User
    ):
        """Test that locked accounts cannot login."""
        login_data = {
            "email": locked_user.email,
            "password": "LockedPass123!",
        }
        
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_423_LOCKED
        assert "locked" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_updates_last_login(
        self, async_client: AsyncClient, existing_user: User, db_session: AsyncSession
    ):
        """Test that successful login updates last_login timestamp."""
        old_last_login = existing_user.last_login
        
        login_data = {
            "email": existing_user.email,
            "password": "ExistingPass123!",
        }
        
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == status.HTTP_200_OK
        
        # Refresh user from database
        await db_session.refresh(existing_user)
        
        # last_login should be updated
        assert existing_user.last_login is not None
        if old_last_login:
            assert existing_user.last_login > old_last_login

    @pytest.mark.asyncio
    async def test_login_resets_failed_attempts(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that successful login resets failed login attempts."""
        # Create user with failed attempts
        user = User(
            email="failedattempts@example.com",
            password_hash=get_password_hash("TestPass123!"),
            full_name="Failed Attempts User",
            failed_login_attempts=3,
        )
        db_session.add(user)
        await db_session.commit()
        
        login_data = {
            "email": user.email,
            "password": "TestPass123!",
        }
        
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == status.HTTP_200_OK
        
        # Refresh user from database
        await db_session.refresh(user)
        
        # Failed attempts should be reset
        assert user.failed_login_attempts == 0

    @pytest.mark.asyncio
    async def test_login_increments_failed_attempts(
        self, async_client: AsyncClient, existing_user: User, db_session: AsyncSession
    ):
        """Test that failed login increments failed_login_attempts."""
        initial_attempts = existing_user.failed_login_attempts
        
        login_data = {
            "email": existing_user.email,
            "password": "WrongPassword123!",
        }
        
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Refresh user from database
        await db_session.refresh(existing_user)
        
        # Failed attempts should be incremented
        assert existing_user.failed_login_attempts == initial_attempts + 1

    @pytest.mark.asyncio
    async def test_login_locks_after_5_failures(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that account is locked after 5 failed login attempts."""
        # Create user with unique email to avoid conflicts with previous test runs
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            email=f"locktest-{unique_id}@example.com",
            password_hash=get_password_hash("CorrectPass123!"),
            full_name="Lock Test User",
        )
        db_session.add(user)
        await db_session.commit()
        
        login_data = {
            "email": user.email,
            "password": "WrongPassword123!",
        }
        
        # Attempt 5 failed logins
        for i in range(5):
            response = await async_client.post("/api/v1/auth/login", json=login_data)
            if i < 4:
                # First 4 attempts should return 401
                assert response.status_code == status.HTTP_401_UNAUTHORIZED
            else:
                # 5th attempt should lock the account and return 423
                assert response.status_code == status.HTTP_423_LOCKED
        
        # Refresh user from database
        await db_session.refresh(user)
        
        # Account should be locked
        assert user.locked_until is not None
        assert user.locked_until > datetime.now(timezone.utc)


# ============================================================================
# Token Refresh Tests
# ============================================================================


@pytest.mark.integration
class TestTokenRefresh:
    """Test token refresh endpoint."""

    @pytest.mark.asyncio
    async def test_refresh_token_success(
        self, async_client: AsyncClient, existing_user: User
    ):
        """Test successful token refresh."""
        # Create a valid refresh token
        refresh_token = create_refresh_token(
            {"sub": existing_user.email, "user_id": str(existing_user.id)}
        )
        
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should return a new access token
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    @pytest.mark.asyncio
    async def test_refresh_with_invalid_token(self, async_client: AsyncClient):
        """Test refresh with invalid token."""
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"},
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_refresh_with_access_token(
        self, async_client: AsyncClient, existing_user: User
    ):
        """Test that refresh endpoint rejects access tokens."""
        # Try to use an access token instead of refresh token
        access_token = create_access_token(
            {"sub": existing_user.email, "user_id": str(existing_user.id)}
        )
        
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token},
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_refresh_with_expired_token(
        self, async_client: AsyncClient, existing_user: User
    ):
        """Test refresh with expired token."""
        # Create an expired refresh token
        from datetime import timedelta
        from jose import jwt
        from app.config import settings
        
        exp = datetime.now(timezone.utc) - timedelta(days=1)
        payload = {
            "sub": existing_user.email,
            "user_id": str(existing_user.id),
            "exp": exp,
            "type": "refresh",
        }
        expired_token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
        
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": expired_token},
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================================
# Protected Endpoint Tests
# ============================================================================


@pytest.mark.integration
class TestProtectedEndpoints:
    """Test authentication-protected endpoints."""

    @pytest.mark.asyncio
    async def test_get_current_user_with_valid_token(
        self, async_client: AsyncClient, existing_user: User
    ):
        """Test accessing protected endpoint with valid token."""
        # Create access token
        access_token = create_access_token(
            {"sub": existing_user.email, "user_id": str(existing_user.id)}
        )
        
        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["email"] == existing_user.email
        assert data["full_name"] == existing_user.full_name
        assert "password" not in data
        assert "password_hash" not in data

    @pytest.mark.asyncio
    async def test_get_current_user_without_token(self, async_client: AsyncClient):
        """Test that protected endpoints reject requests without tokens."""
        response = await async_client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_get_current_user_with_invalid_token(self, async_client: AsyncClient):
        """Test that protected endpoints reject invalid tokens."""
        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_current_user_with_expired_token(
        self, async_client: AsyncClient, existing_user: User
    ):
        """Test that expired tokens are rejected."""
        # Create expired token
        from jose import jwt
        from app.config import settings
        
        exp = datetime.now(timezone.utc) - timedelta(minutes=1)
        payload = {
            "sub": existing_user.email,
            "user_id": str(existing_user.id),
            "exp": exp,
            "type": "access",
        }
        expired_token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
        
        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================================
# Password Change Tests
# ============================================================================


@pytest.mark.integration
class TestPasswordChange:
    """Test password change endpoint."""

    @pytest.mark.asyncio
    async def test_change_password_success(
        self, async_client: AsyncClient, existing_user: User, db_session: AsyncSession
    ):
        """Test successful password change."""
        # Get access token
        access_token = create_access_token(
            {"sub": existing_user.email, "user_id": str(existing_user.id)}
        )
        
        old_password_hash = existing_user.password_hash
        
        response = await async_client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "current_password": "ExistingPass123!",
                "new_password": "NewSecurePass123!",
            },
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Refresh user from database
        await db_session.refresh(existing_user)
        
        # Password hash should have changed
        assert existing_user.password_hash != old_password_hash

    @pytest.mark.asyncio
    async def test_change_password_incorrect_current(
        self, async_client: AsyncClient, existing_user: User
    ):
        """Test password change with incorrect current password."""
        access_token = create_access_token(
            {"sub": existing_user.email, "user_id": str(existing_user.id)}
        )
        
        response = await async_client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "current_password": "WrongPassword123!",
                "new_password": "NewSecurePass123!",
            },
        )
        
        # Endpoint returns 401 for incorrect current password
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_change_password_weak_new_password(
        self, async_client: AsyncClient, existing_user: User
    ):
        """Test that weak new passwords are rejected."""
        access_token = create_access_token(
            {"sub": existing_user.email, "user_id": str(existing_user.id)}
        )
        
        response = await async_client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "current_password": "ExistingPass123!",
                "new_password": "weak",
            },
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_change_password_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Test that password change requires authentication."""
        response = await async_client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "OldPass123!",
                "new_password": "NewPass123!",
            },
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ============================================================================
# Logout Tests
# ============================================================================


@pytest.mark.integration
class TestLogout:
    """Test logout endpoint."""

    @pytest.mark.asyncio
    async def test_logout_success(
        self, async_client: AsyncClient, existing_user: User
    ):
        """Test successful logout."""
        access_token = create_access_token(
            {"sub": existing_user.email, "user_id": str(existing_user.id)}
        )
        refresh_token = create_refresh_token(
            {"sub": existing_user.email, "user_id": str(existing_user.id)}
        )
        
        response = await async_client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"refresh_token": refresh_token},
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()

    @pytest.mark.asyncio
    async def test_logout_requires_authentication(self, async_client: AsyncClient):
        """Test that logout requires authentication."""
        response = await async_client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": "some.refresh.token"},
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

