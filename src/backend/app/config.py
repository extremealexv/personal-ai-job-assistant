"""Application configuration using Pydantic Settings."""

from pathlib import Path
from typing import Any, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Find project root (where .env should be)
def get_project_root() -> Path:
    """Get the project root directory (3 levels up from this file).

    Path structure:
    - This file: src/backend/app/config.py
    - Parent: src/backend/app/
    - Parent.parent: src/backend/
    - Parent.parent.parent: src/
    - Parent.parent.parent.parent: project root
    """
    return Path(__file__).parent.parent.parent.parent


# Path to .env file in project root
ENV_FILE = get_project_root() / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
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
    gmail_client_id: Optional[str] = Field(default=None, description="Gmail OAuth client ID")
    secret_key: str = Field(..., description="Secret key for session management and JWT")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    app_env: str = Field(
        default="development", description="Environment: development, staging, production"
    )

    # Security & Encryption
    encryption_key: str = Field(..., description="Fernet encryption key for sensitive data")

    # JWT Authentication
    algorithm: str = Field(default="HS256", description="JWT signing algorithm")
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration time in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7, description="Refresh token expiration time in days"
    )

    # AI Service Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(default="gpt-4", description="Default OpenAI model")
    openai_max_tokens: int = Field(default=4000, description="Max tokens per request")
    openai_temperature: float = Field(default=0.7, description="Default temperature for completions")
    openai_timeout: int = Field(default=30, description="OpenAI API timeout in seconds")
    openai_max_retries: int = Field(default=3, description="Max retries for OpenAI API calls")
    
    # AI Rate Limiting
    ai_requests_per_minute: int = Field(
        default=10, description="Max AI API requests per minute per user"
    )
    ai_requests_per_day: int = Field(
        default=100, description="Max AI API requests per day per user"
    )
    
    # AI Cost Tracking
    openai_cost_per_1k_prompt_tokens: float = Field(
        default=0.03, description="Cost per 1000 prompt tokens (GPT-4)"
    )
    openai_cost_per_1k_completion_tokens: float = Field(
        default=0.06, description="Cost per 1000 completion tokens (GPT-4)"
    )
    ai_monthly_budget_limit: float = Field(
        default=100.0, description="Monthly AI API budget limit in USD"
    )

    # OAuth & External Services
    gmail_client_secret: Optional[str] = Field(
        default=None, description="Gmail OAuth client secret"
    )
    google_calendar_client_id: Optional[str] = Field(
        default=None, description="Google Calendar OAuth client ID"
    )
    google_calendar_client_secret: Optional[str] = Field(
        default=None, description="Google Calendar OAuth client secret"
    )

    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="Allowed CORS origins (comma-separated)",
    )

    # Session Configuration
    session_timeout_hours: int = Field(default=24, description="Session timeout in hours")
    session_cookie_secure: bool = Field(
        default=False,
        description="Use secure cookies (HTTPS only in production)",
    )

    # File Upload Configuration
    max_upload_size_mb: int = Field(default=10, description="Maximum file upload size in MB")
    upload_dir: Path = Field(default=Path("./uploads"), description="Directory for uploaded files")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, description="API rate limit per minute")

    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        return [self.cors_origins]

    @field_validator("upload_dir", mode="before")
    @classmethod
    def parse_upload_dir(cls, v: Any) -> Path:
        """Convert upload directory to Path object."""
        if isinstance(v, str):
            return Path(v)
        if isinstance(v, Path):
            return v
        return Path(str(v))

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


# Helper function to initialize settings with better error messages
def load_settings() -> Settings:
    """Load settings with helpful error messages."""
    try:
        return Settings()  # type: ignore[call-arg]
    except Exception as e:
        if "validation error" in str(e).lower():
            print("\nConfiguration Error: Missing required environment variables")
            print(f"\nLooking for .env file at: {ENV_FILE}")
            print(f"   File exists: {ENV_FILE.exists()}")

            if not ENV_FILE.exists():
                print("\nQuick fix:")
                print("   1. Copy the template: cp .env.example .env")
                print("   2. Run setup script: " "cd src/backend && python scripts/setup_env.ps1")
                print("   3. Edit .env with your credentials")
            else:
                print("\nThe .env file exists but is missing required values.")
                print("   Check that these variables are set:")
                print("   - DATABASE_URL")
                print("   - DATABASE_ASYNC_URL")
                print("   - SECRET_KEY")
                print("   - ENCRYPTION_KEY")
                print("   - OPENAI_API_KEY")
            print()
        raise


# Global settings instance
settings = load_settings()

# Create upload directory on startup
settings.create_upload_dir()
