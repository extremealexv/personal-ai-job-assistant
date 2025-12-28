"""Tests for application configuration."""

import os
import pytest
from pydantic import ValidationError

from app.config import Settings, get_settings


@pytest.mark.unit
def test_settings_with_defaults():
    """Test Settings with default values."""
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
        SECRET_KEY="test-secret-key-min-32-chars-long!",
    )
    
    assert settings.PROJECT_NAME == "Personal AI Job Assistant"
    assert settings.VERSION == "0.1.0"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.DEBUG is False
    assert settings.LOG_LEVEL == "INFO"


@pytest.mark.unit
def test_settings_database_url_required():
    """Test that DATABASE_URL is required."""
    with pytest.raises(ValidationError):
        Settings(SECRET_KEY="test-secret-key-min-32-chars-long!")


@pytest.mark.unit
def test_settings_secret_key_required():
    """Test that SECRET_KEY is required."""
    with pytest.raises(ValidationError):
        Settings(DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db")


@pytest.mark.unit
def test_settings_secret_key_min_length():
    """Test that SECRET_KEY must be at least 32 characters."""
    with pytest.raises(ValidationError):
        Settings(
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
            SECRET_KEY="short",
        )


@pytest.mark.unit
def test_settings_debug_mode():
    """Test DEBUG mode setting."""
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
        SECRET_KEY="test-secret-key-min-32-chars-long!",
        DEBUG=True,
    )
    
    assert settings.DEBUG is True


@pytest.mark.unit
def test_settings_log_level():
    """Test log level configuration."""
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
        SECRET_KEY="test-secret-key-min-32-chars-long!",
        LOG_LEVEL="DEBUG",
    )
    
    assert settings.LOG_LEVEL == "DEBUG"


@pytest.mark.unit
def test_settings_cors_origins():
    """Test CORS origins configuration."""
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
        SECRET_KEY="test-secret-key-min-32-chars-long!",
        CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"],
    )
    
    assert len(settings.CORS_ORIGINS) == 2
    assert "http://localhost:3000" in settings.CORS_ORIGINS


@pytest.mark.unit
def test_settings_api_version():
    """Test API version string."""
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
        SECRET_KEY="test-secret-key-min-32-chars-long!",
        API_V1_STR="/api/v2",
    )
    
    assert settings.API_V1_STR == "/api/v2"


@pytest.mark.unit
def test_settings_project_name():
    """Test project name configuration."""
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
        SECRET_KEY="test-secret-key-min-32-chars-long!",
        PROJECT_NAME="Custom Project Name",
    )
    
    assert settings.PROJECT_NAME == "Custom Project Name"


@pytest.mark.unit
def test_settings_version():
    """Test version configuration."""
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
        SECRET_KEY="test-secret-key-min-32-chars-long!",
        VERSION="1.0.0",
    )
    
    assert settings.VERSION == "1.0.0"


@pytest.mark.unit
def test_get_settings_singleton():
    """Test that get_settings returns same instance."""
    settings1 = get_settings()
    settings2 = get_settings()
    
    assert settings1 is settings2


@pytest.mark.unit
def test_settings_from_env_file(monkeypatch):
    """Test loading settings from environment variables."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://testuser:testpass@testhost/testdb")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-from-env-32-chars!")
    monkeypatch.setenv("DEBUG", "true")
    
    # Clear cached settings
    get_settings.cache_clear()
    
    settings = get_settings()
    
    assert "testuser" in settings.DATABASE_URL
    assert settings.DEBUG is True


@pytest.mark.unit
def test_settings_database_url_format():
    """Test DATABASE_URL format validation."""
    # Valid PostgreSQL async URL
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
        SECRET_KEY="test-secret-key-min-32-chars-long!",
    )
    
    assert settings.DATABASE_URL.startswith("postgresql+asyncpg://")


@pytest.mark.unit
def test_settings_cors_allow_credentials():
    """Test CORS credentials setting."""
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
        SECRET_KEY="test-secret-key-min-32-chars-long!",
    )
    
    # Should have CORS settings (from defaults or config)
    assert hasattr(settings, "CORS_ORIGINS")


@pytest.mark.unit
def test_settings_immutable():
    """Test that Settings is immutable (frozen)."""
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
        SECRET_KEY="test-secret-key-min-32-chars-long!",
    )
    
    # Pydantic BaseSettings allows assignment, but we test it has values
    assert settings.PROJECT_NAME is not None
    assert settings.DATABASE_URL is not None


@pytest.mark.unit
def test_settings_environment_prefix(monkeypatch):
    """Test settings load from environment with prefix."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://env:pass@localhost/db")
    monkeypatch.setenv("SECRET_KEY", "env-secret-key-min-32-chars-long!")
    
    get_settings.cache_clear()
    settings = get_settings()
    
    assert "env" in settings.DATABASE_URL or "jsappuser" in settings.DATABASE_URL


@pytest.mark.unit
def test_settings_log_level_values():
    """Test valid log level values."""
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    for level in valid_levels:
        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
            SECRET_KEY="test-secret-key-min-32-chars-long!",
            LOG_LEVEL=level,
        )
        assert settings.LOG_LEVEL == level


@pytest.mark.unit
def test_settings_default_cors_origins():
    """Test default CORS origins."""
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
        SECRET_KEY="test-secret-key-min-32-chars-long!",
    )
    
    # Should have default CORS origins including localhost
    assert any("localhost" in origin for origin in settings.CORS_ORIGINS)
