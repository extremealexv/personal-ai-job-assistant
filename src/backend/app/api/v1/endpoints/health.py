"""Health check endpoints."""

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    version: str
    environment: str


class DatabaseHealthResponse(BaseModel):
    """Database health check response."""

    status: str
    connected: bool
    message: str


@router.get("", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check() -> HealthResponse:
    """Main health check endpoint.
    
    Returns basic application status and version information.
    """
    from app.config import settings
    
    return HealthResponse(
        status="ok",
        version="0.1.0",
        environment=settings.app_env,
    )


@router.get("/db", response_model=DatabaseHealthResponse, status_code=status.HTTP_200_OK)
async def database_health() -> DatabaseHealthResponse:
    """Database health check endpoint.
    
    Tests database connectivity and returns connection status.
    """
    # TODO: Implement actual database connection test
    # For now, return a placeholder response
    return DatabaseHealthResponse(
        status="ok",
        connected=False,
        message="Database health check not yet implemented",
    )
