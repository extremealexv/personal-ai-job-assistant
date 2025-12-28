"""FastAPI application main module."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.config import settings
from app.core.error_handlers import (
    api_exception_handler,
    general_exception_handler,
    integrity_error_handler,
    sqlalchemy_error_handler,
    validation_exception_handler,
)
from app.core.exceptions import APIException
from app.core.logging import setup_logging
from app.core.middleware import (
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from app.db import check_db_connection


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown events.
    
    This function handles initialization and cleanup:
    - Startup: Initialize database connections, logging, etc.
    - Shutdown: Close connections gracefully
    """
    # Startup logic
    setup_logging()
    print("🚀 Starting Personal AI Job Assistant API...")
    print(f"📍 Environment: {settings.app_env}")
    print(f"🔧 Debug mode: {settings.debug}")
    print(f"📦 Upload directory: {settings.upload_dir}")
    
    # Check database connection
    db_connected = await check_db_connection()
    if db_connected:
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
    
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

# Add custom middleware (order matters - last added is executed first)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIDMiddleware)


# Global exception handlers - use new centralized handlers
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
app.add_exception_handler(Exception, general_exception_handler)


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
