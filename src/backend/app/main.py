"""FastAPI application main module."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown events.
    
    This function handles initialization and cleanup:
    - Startup: Initialize database connections, Redis, etc.
    - Shutdown: Close connections gracefully
    """
    # Startup logic
    print("🚀 Starting Personal AI Job Assistant API...")
    print(f"📍 Environment: {settings.app_env}")
    print(f"🔧 Debug mode: {settings.debug}")
    print(f"📦 Upload directory: {settings.upload_dir}")
    
    # TODO: Initialize database connection pool
    # TODO: Initialize Redis connection
    # TODO: Initialize AI service clients
    
    yield
    
    # Shutdown logic
    print("🛑 Shutting down API...")
    # TODO: Close database connections
    # TODO: Close Redis connection
    # TODO: Cleanup resources


# Initialize FastAPI application
app = FastAPI(
    title="Personal AI Job Assistant API",
    description="AI-powered job application management system with resume tailoring and automation",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors with detailed error messages."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "message": "Validation error",
            "path": str(request.url),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions."""
    # Log the error (TODO: integrate with proper logging)
    print(f"❌ Unhandled exception: {exc}")
    
    # Don't expose internal errors in production
    if settings.is_production:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "message": "An unexpected error occurred",
            },
        )
    
    # Show detailed errors in development
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": str(exc),
            "message": "Internal server error",
            "type": type(exc).__name__,
        },
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """Root endpoint - API information."""
    return {
        "message": "Personal AI Job Assistant API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


# Health check endpoint (basic)
@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


# Include API routers
from app.api.v1.api import api_router

app.include_router(api_router, prefix="/api/v1")
