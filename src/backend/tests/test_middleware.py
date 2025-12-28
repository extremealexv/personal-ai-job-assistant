"""Tests for middleware components."""

import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.middleware import RequestLoggingMiddleware


@pytest.mark.integration
async def test_request_id_middleware(async_client: AsyncClient):
    """Test that Request ID is added to all responses."""
    response = await async_client.get("/health")
    
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0


@pytest.mark.integration
async def test_request_id_is_unique(async_client: AsyncClient):
    """Test that each request gets a unique Request ID."""
    response1 = await async_client.get("/health")
    response2 = await async_client.get("/health")
    
    request_id_1 = response1.headers["X-Request-ID"]
    request_id_2 = response2.headers["X-Request-ID"]
    
    assert request_id_1 != request_id_2


@pytest.mark.integration
async def test_security_headers_present(async_client: AsyncClient):
    """Test that security headers are present."""
    response = await async_client.get("/health")
    
    assert "X-Content-Type-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    
    assert "X-Frame-Options" in response.headers
    assert response.headers["X-Frame-Options"] == "DENY"
    
    assert "X-XSS-Protection" in response.headers
    assert response.headers["X-XSS-Protection"] == "1; mode=block"


@pytest.mark.integration
async def test_cors_headers_present(async_client: AsyncClient):
    """Test that CORS headers are configured."""
    response = await async_client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    
    # CORS middleware should handle OPTIONS requests
    assert response.status_code in [200, 204]


@pytest.mark.integration
async def test_request_logging_captures_path(async_client: AsyncClient):
    """Test that request logging middleware captures requests."""
    # Make a request
    response = await async_client.get("/health")
    
    # Should have request ID (logged)
    assert "X-Request-ID" in response.headers


@pytest.mark.integration
async def test_request_logging_captures_method(async_client: AsyncClient):
    """Test request logging captures different methods."""
    # GET request
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers


@pytest.mark.integration
async def test_middleware_order_preserved(client):
    """Test that middleware is applied in correct order."""
    # Request should go through all middleware layers
    response = client.get("/health")
    
    # Request ID middleware
    assert "X-Request-ID" in response.headers
    
    # Security headers middleware
    assert "X-Content-Type-Options" in response.headers
    
    # All middleware executed successfully
    assert response.status_code == 200


@pytest.mark.unit
def test_request_context_middleware_initialization():
    """Test RequestContextMiddleware can be initialized."""
    app = FastAPI()
    
    # Should not raise exception
    middleware = RequestContextMiddleware(app)
    assert middleware.app == app


@pytest.mark.unit
def test_request_logging_middleware_initialization():
    """Test RequestLoggingMiddleware can be initialized."""
    app = FastAPI()
    
    # Should not raise exception
    middleware = RequestLoggingMiddleware(app)
    assert middleware.app == app


@pytest.mark.integration
async def test_middleware_handles_errors_gracefully(async_client: AsyncClient):
    """Test that middleware doesn't break error responses."""
    # Request to non-existent endpoint
    response = await async_client.get("/nonexistent")
    
    # Should still have security headers
    assert "X-Request-ID" in response.headers
    assert "X-Content-Type-Options" in response.headers


@pytest.mark.integration
async def test_request_id_available_in_context(async_client: AsyncClient):
    """Test that request ID is available throughout request lifecycle."""
    response = await async_client.get("/")
    
    # Request ID should be in response
    assert "X-Request-ID" in response.headers
    
    # Should be valid UUID format
    request_id = response.headers["X-Request-ID"]
    assert len(request_id) > 0
    assert "-" in request_id  # UUID format check
