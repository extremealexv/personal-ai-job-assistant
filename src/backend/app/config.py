"""Application configuration using Pydantic Settings."""
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database Configuration
    database_url: str = Field(
        ...,
        description="PostgreSQL connection URL",
        examples=["postgresql://user:pass@localhost:5432/dbname"],
    )
    database_async_url: str = Field(
        ...,
        description="PostgreSQL async connection URL",
        examples=["postgresql+asyncpg://user:pass@localhost:5432/dbname"],
    )

    # Redis Configuration
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )

    # Application Configuration
    app_env: str = Field(default="development", description="Environment: development, staging, production")
    secret_key: str = Field(..., description="Secret key for session management and JWT")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # Security & Encryption
    encryption_key: str = Field(..., description="Fernet encryption key for sensitive data")

    # AI Service Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(default="gpt-4", description="Default OpenAI model")
    openai_max_tokens: int = Field(default=4000, description="Max tokens per request")

    # OAuth & External Services
    gmail_client_id: Optional[str] = Field(default=None, description="Gmail OAuth client ID")
    gmail_client_secret: Optional[str] = Field(default=None, description="Gmail OAuth client secret")
    google_calendar_client_id: Optional[str] = Field(default=None, description="Google Calendar OAuth client ID")
    google_calendar_client_secret: Optional[str] = Field(
        default=None, description="Google Calendar OAuth client secret"
    )

    # CORS Configuration
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origins",
    )

    # Session Configuration
    session_timeout_hours: int = Field(default=24, description="Session timeout in hours")
    session_cookie_secure: bool = Field(
        default=False, description="Use secure cookies (HTTPS only in production)"
    )

    # File Upload Configuration
    max_upload_size_mb: int = Field(default=10, description="Maximum file upload size in MB")
    upload_dir: Path = Field(default=Path("./uploads"), description="Directory for uploaded files")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, description="API rate limit per minute")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("upload_dir", mode="before")
    @classmethod
    def parse_upload_dir(cls, v):
        """Convert upload directory to Path object."""
        if isinstance(v, str):
            return Path(v)
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env == "development"

    def create_upload_dir(self) -> None:
        """Create upload directory if it doesn't exist."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

# Create upload directory on startup
settings.create_upload_dir()
