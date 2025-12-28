"""Tests for application configuration."""

import os
import pytest
from pydantic import ValidationError

from app.config import Settings, settings


@pytest.mark.unit
def test_settings_with_defaults():
    """Test Settings with default values."""
    test_settings = Settings(
        database_url="postgresql://user:pass@localhost/db",
        database_async_url="postgresql+asyncpg://user:pass@localhost/db",
        secret_key="test-secret-key-min-32-chars-long!",
        encryption_key="test-encryption-key-min-32-chars!",
        openai_api_key="test-openai-key",
    )
    
    assert test_settings.project_name == "Personal AI Job Assistant API"
    assert test_settings.version == "0.1.0"
    assert test_settings.api_v1_str == "/api/v1"
    assert test_settings.debug is False


@pytest.mark.unit
def test_settings_database_url_required():
    """Test that database_url is required."""
    with pytest.raises(ValidationError):
        Settings(
            secret_key="test-secret-key-min-32-chars-long!",
            encryption_key="test-encryption-key-min-32-chars!",
            openai_api_key="test-key",
        )


@pytest.mark.unit
def test_settings_secret_key_required():
    """Test that secret_key is required."""
    with pytest.raises(ValidationError):
        Settings(
            database_url="postgresql://user:pass@localhost/db",
            database_async_url="postgresql+asyncpg://user:pass@localhost/db",
        )


@pytest.mark.unit
def test_settings_secret_key_min_length():
    """Test that secret_key must be at least 32 characters."""
    with pytest.raises(ValidationError):
        Settings(
            database_url="postgresql://user:pass@localhost/db",
            database_async_url="postgresql+asyncpg://user:pass@localhost/db",
            secret_key="short",
            encryption_key="test-encryption-key-min-32-chars!",
            openai_api_key="test-key",
        )


@pytest.mark.unit
def test_settings_debug_mode():
    """Test debug mode setting."""
    test_settings = Settings(
        database_url="postgresql://user:pass@localhost/db",
        database_async_url="postgresql+asyncpg://user:pass@localhost/db",
        secret_key="test-secret-key-min-32-chars-long!",
        encryption_key="test-encryption-key-min-32-chars!",
        openai_api_key="test-key",
        debug=True,
    )
    
    assert test_settings.debug is True


@pytest.mark.unit
def test_settings_api_version():
    """Test API version string."""
    test_settings = Settings(
        database_url="postgresql://user:pass@localhost/db",
        database_async_url="postgresql+asyncpg://user:pass@localhost/db",
        secret_key="test-secret-key-min-32-chars-long!",
        encryption_key="test-encryption-key-min-32-chars!",
        openai_api_key="test-key",
        api_v1_str="/api/v2",
    )
    
    assert test_settings.api_v1_str == "/api/v2"


@pytest.mark.unit
def test_settings_project_name():
    """Test project name configuration."""
    test_settings = Settings(
        database_url="postgresql://user:pass@localhost/db",
        database_async_url="postgresql+asyncpg://user:pass@localhost/db",
        secret_key="test-secret-key-min-32-chars-long!",
        encryption_key="test-encryption-key-min-32-chars!",
        openai_api_key="test-key",
        project_name="Custom Project Name",
    )
    
    assert test_settings.project_name == "Custom Project Name"


@pytest.mark.unit
def test_settings_version():
    """Test version configuration."""
    test_settings = Settings(
        database_url="postgresql://user:pass@localhost/db",
        database_async_url="postgresql+asyncpg://user:pass@localhost/db",
        secret_key="test-secret-key-min-32-chars-long!",
        encryption_key="test-encryption-key-min-32-chars!",
        openai_api_key="test-key",
        version="1.0.0",
    )
    
    assert test_settings.version == "1.0.0"


@pytest.mark.unit
def test_settings_is_singleton():
    """Test that settings is a global singleton instance."""
    from app.config import settings as settings1
    from app.config import settings as settings2
    
    assert settings1 is settings2


@pytest.mark.unit
def test_settings_loaded_from_env():
    """Test that settings are loaded from environment."""
    # Settings already loaded from .env file
    assert settings.database_url is not None
    assert settings.database_async_url is not None
    assert settings.secret_key is not None
    assert len(settings.secret_key) >= 32


@pytest.mark.unit
def test_settings_database_url_format():
    """Test database_url format validation."""
    # Valid PostgreSQL URL
    test_settings = Settings(
        database_url="postgresql://user:pass@localhost:5432/db",
        database_async_url="postgresql+asyncpg://user:pass@localhost:5432/db",
        secret_key="test-secret-key-min-32-chars-long!",
        encryption_key="test-encryption-key-min-32-chars!",
        openai_api_key="test-key",
    )
    
    assert test_settings.database_url.startswith("postgresql://")


@pytest.mark.unit
def test_settings_has_required_fields():
    """Test that loaded settings has all required fields."""
    assert hasattr(settings, "database_url")
    assert hasattr(settings, "database_async_url")
    assert hasattr(settings, "secret_key")
    assert hasattr(settings, "project_name")
    assert hasattr(settings, "version")
    assert hasattr(settings, "api_v1_str")

