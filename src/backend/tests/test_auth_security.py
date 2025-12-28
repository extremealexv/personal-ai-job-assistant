"""Unit tests for authentication security functions."""

import re
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from jose import jwt

from app.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    is_valid_password,
    verify_password,
    verify_token,
)


# ============================================================================
# Password Hashing Tests
# ============================================================================


@pytest.mark.unit
class TestPasswordHashing:
    """Test password hashing and verification functions."""

    def test_get_password_hash_creates_valid_hash(self):
        """Test that password hashing creates a valid bcrypt hash."""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)
        
        # Bcrypt hashes should start with $2b$ (our configured ident)
        assert hashed.startswith("$2b$")
        # Bcrypt hashes are 60 characters long
        assert len(hashed) == 60

    def test_get_password_hash_different_hashes_for_same_password(self):
        """Test that hashing the same password twice produces different hashes (salt)."""
        password = "SamePassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2  # Different salts

    def test_verify_password_correct_password(self):
        """Test that verify_password returns True for correct password."""
        password = "CorrectPassword123!"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect_password(self):
        """Test that verify_password returns False for incorrect password."""
        password = "CorrectPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive."""
        password = "CaseSensitive123!"
        hashed = get_password_hash(password)
        
        assert verify_password("casesensitive123!", hashed) is False
        assert verify_password("CASESENSITIVE123!", hashed) is False

    def test_password_with_special_characters(self):
        """Test password hashing with various special characters."""
        special_passwords = [
            "Password!@#$%^&*()",
            "Pass-word_123",
            "Pāsswörd123",  # Unicode
            "Password with spaces!1",
        ]
        
        for password in special_passwords:
            hashed = get_password_hash(password)
            assert verify_password(password, hashed) is True

    def test_password_truncation_at_72_bytes(self):
        """Test that passwords longer than 72 bytes are truncated."""
        # Create a password that's >72 bytes when encoded
        long_password = "A" * 100  # 100 ASCII characters = 100 bytes
        hashed = get_password_hash(long_password)
        
        # First 72 bytes should match
        truncated = "A" * 72
        assert verify_password(truncated, hashed) is True

    def test_empty_password_handling(self):
        """Test handling of empty password."""
        # Should not crash, but also shouldn't be used in practice
        hashed = get_password_hash("")
        assert verify_password("", hashed) is True


# ============================================================================
# Password Validation Tests
# ============================================================================


@pytest.mark.unit
class TestPasswordValidation:
    """Test password validation rules."""

    def test_valid_password(self):
        """Test that valid passwords pass validation."""
        valid_passwords = [
            "Password123!",
            "SecureP@ss1",
            "MyP@ssw0rd",
            "C0mplex!Pass",
        ]
        
        for password in valid_passwords:
            assert is_valid_password(password) is True, f"Failed for: {password}"

    def test_password_too_short(self):
        """Test that passwords shorter than 8 characters fail."""
        assert is_valid_password("Pass1!") is False  # 6 chars
        assert is_valid_password("Pass12!") is False  # 7 chars

    def test_password_no_uppercase(self):
        """Test that passwords without uppercase letters fail."""
        assert is_valid_password("password123!") is False

    def test_password_no_lowercase(self):
        """Test that passwords without lowercase letters fail."""
        assert is_valid_password("PASSWORD123!") is False

    def test_password_no_digit(self):
        """Test that passwords without digits fail."""
        assert is_valid_password("Password!") is False

    def test_password_no_special_char(self):
        """Test that passwords without special characters fail."""
        assert is_valid_password("Password123") is False

    def test_password_minimum_length(self):
        """Test that 8-character password with all requirements passes."""
        assert is_valid_password("Pass123!") is True  # Exactly 8 chars

    def test_password_with_spaces(self):
        """Test that passwords with spaces are accepted if they meet other requirements."""
        assert is_valid_password("Pass Word123!") is True


# ============================================================================
# JWT Token Creation Tests
# ============================================================================


@pytest.mark.unit
class TestJWTCreation:
    """Test JWT token creation functions."""

    def test_create_access_token_basic(self):
        """Test creating a basic access token."""
        data = {"sub": "test@example.com", "user_id": "123"}
        token = create_access_token(data)
        
        # Token should be non-empty string
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify payload
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == "123"
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_create_access_token_default_expiration(self):
        """Test that access token has correct default expiration."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        # Should expire in approximately 30 minutes (allow 1 second tolerance)
        expected_exp = now + timedelta(minutes=settings.access_token_expire_minutes)
        assert abs((exp - expected_exp).total_seconds()) < 2

    def test_create_access_token_custom_expiration(self):
        """Test creating access token with custom expiration."""
        data = {"sub": "test@example.com"}
        custom_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=custom_delta)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        # Should expire in approximately 60 minutes
        expected_exp = now + custom_delta
        assert abs((exp - expected_exp).total_seconds()) < 2

    def test_create_refresh_token_basic(self):
        """Test creating a basic refresh token."""
        data = {"sub": "test@example.com", "user_id": "123"}
        token = create_refresh_token(data)
        
        # Token should be non-empty string
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify payload
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == "123"
        assert payload["type"] == "refresh"
        assert "exp" in payload

    def test_create_refresh_token_expiration(self):
        """Test that refresh token has correct expiration (7 days)."""
        data = {"sub": "test@example.com"}
        token = create_refresh_token(data)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        # Should expire in approximately 7 days (allow 2 second tolerance)
        expected_exp = now + timedelta(days=settings.refresh_token_expire_days)
        assert abs((exp - expected_exp).total_seconds()) < 2

    def test_tokens_use_configured_algorithm(self):
        """Test that tokens use the configured JWT algorithm."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        # Decode header to check algorithm
        header = jwt.get_unverified_header(token)
        assert header["alg"] == settings.algorithm


# ============================================================================
# JWT Token Verification Tests
# ============================================================================


@pytest.mark.unit
class TestJWTVerification:
    """Test JWT token verification functions."""

    def test_verify_valid_access_token(self):
        """Test verifying a valid access token."""
        data = {"sub": "test@example.com", "user_id": "123"}
        token = create_access_token(data)
        
        payload = verify_token(token, "access")
        assert payload is not None
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == "123"
        assert payload["type"] == "access"

    def test_verify_valid_refresh_token(self):
        """Test verifying a valid refresh token."""
        data = {"sub": "test@example.com", "user_id": "123"}
        token = create_refresh_token(data)
        
        payload = verify_token(token, "refresh")
        assert payload is not None
        assert payload["sub"] == "test@example.com"
        assert payload["type"] == "refresh"

    def test_verify_wrong_token_type(self):
        """Test that verifying with wrong token type returns None."""
        data = {"sub": "test@example.com"}
        access_token = create_access_token(data)
        
        # Try to verify as refresh token
        payload = verify_token(access_token, "refresh")
        assert payload is None

    def test_verify_expired_token(self):
        """Test that expired tokens return None."""
        data = {"sub": "test@example.com"}
        # Create token that expires immediately
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        payload = verify_token(token, "access")
        assert payload is None

    def test_verify_invalid_signature(self):
        """Test that tokens with invalid signatures return None."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        # Tamper with the token
        parts = token.split(".")
        tampered_token = ".".join([parts[0], parts[1], "invalid_signature"])
        
        payload = verify_token(tampered_token, "access")
        assert payload is None

    def test_verify_malformed_token(self):
        """Test that malformed tokens return None."""
        malformed_tokens = [
            "not.a.token",
            "invalid",
            "",
            "eyJ.incomplete",
        ]
        
        for token in malformed_tokens:
            payload = verify_token(token, "access")
            assert payload is None, f"Should reject malformed token: {token}"

    def test_verify_token_without_type(self):
        """Test verifying token that doesn't have a type field."""
        # Create token manually without type field
        data = {"sub": "test@example.com"}
        exp = datetime.now(timezone.utc) + timedelta(minutes=30)
        payload_data = {**data, "exp": exp}
        token = jwt.encode(payload_data, settings.secret_key, algorithm=settings.algorithm)
        
        # Should return None because type is missing
        payload = verify_token(token, "access")
        assert payload is None


# ============================================================================
# Edge Cases and Security Tests
# ============================================================================


@pytest.mark.unit
class TestSecurityEdgeCases:
    """Test edge cases and security considerations."""

    def test_password_hash_consistency(self):
        """Test that the same password always verifies against its hash."""
        password = "ConsistentPassword123!"
        hashed = get_password_hash(password)
        
        # Verify multiple times
        for _ in range(10):
            assert verify_password(password, hashed) is True

    def test_token_uniqueness(self):
        """Test that creating multiple tokens produces unique tokens."""
        import time
        data = {"sub": "test@example.com"}
        tokens = []
        for _ in range(10):
            tokens.append(create_access_token(data))
            time.sleep(0.001)  # Small delay to ensure different timestamps
        
        # All tokens should be unique (different expiration times)
        assert len(set(tokens)) == len(tokens)

    def test_password_with_null_bytes(self):
        """Test handling of passwords with null bytes."""
        # This is a security consideration - ensure null bytes don't truncate
        password = "Pass\x00word123!"
        hashed = get_password_hash(password)
        
        # The full password should be required, not just up to null byte
        assert verify_password("Pass", hashed) is False
        assert verify_password(password, hashed) is True

    def test_unicode_password_handling(self):
        """Test that unicode passwords are handled correctly."""
        unicode_passwords = [
            "Pāsswörd123!",  # Latin extended
            "密码Password123!",  # Chinese characters
            "Пароль123!",  # Cyrillic
            "🔐Password123!",  # Emoji
        ]
        
        for password in unicode_passwords:
            hashed = get_password_hash(password)
            assert verify_password(password, hashed) is True

    def test_jwt_claims_not_modifiable(self):
        """Test that JWT claims cannot be modified without detection."""
        data = {"sub": "test@example.com", "user_id": "123"}
        token = create_access_token(data)
        
        # Decode and verify original token
        payload = verify_token(token, "access")
        assert payload["user_id"] == "123"
        
        # Try to manually modify the payload without proper signing
        # Split token into parts
        parts = token.split(".")
        # Tamper with payload by modifying encoded data
        import base64
        import json
        payload_decoded = json.loads(base64.urlsafe_b64decode(parts[1] + "===" ))
        payload_decoded["user_id"] = "456"
        tampered_payload = base64.urlsafe_b64encode(
            json.dumps(payload_decoded).encode()
        ).decode().rstrip("=")
        tampered_token = f"{parts[0]}.{tampered_payload}.{parts[2]}"
        
        # The tampered token should be rejected (invalid signature)
        result = verify_token(tampered_token, "access")
        assert result is None


# ============================================================================
# Performance Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.slow
class TestSecurityPerformance:
    """Test performance characteristics of security functions."""

    def test_password_hashing_speed(self):
        """Test that password hashing completes in reasonable time."""
        import time
        
        password = "TestPassword123!"
        start = time.time()
        get_password_hash(password)
        duration = time.time() - start
        
        # Bcrypt with 12 rounds should take 100-500ms
        # Allow up to 1 second for slower systems
        assert duration < 1.0, f"Password hashing took {duration:.3f}s, expected < 1s"

    def test_password_verification_speed(self):
        """Test that password verification completes in reasonable time."""
        import time
        
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        start = time.time()
        verify_password(password, hashed)
        duration = time.time() - start
        
        # Verification should be similar to hashing
        assert duration < 1.0, f"Password verification took {duration:.3f}s, expected < 1s"

    def test_token_creation_speed(self):
        """Test that token creation is fast."""
        import time
        
        data = {"sub": "test@example.com", "user_id": "123"}
        
        start = time.time()
        for _ in range(100):
            create_access_token(data)
        duration = time.time() - start
        
        # Creating 100 tokens should take less than 100ms
        assert duration < 0.1, f"Creating 100 tokens took {duration:.3f}s, expected < 0.1s"
