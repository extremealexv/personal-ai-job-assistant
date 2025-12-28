"""Unit tests for health check endpoints."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_root_endpoint(client: TestClient):
    """Test root endpoint returns API information."""
    response = client.get("/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "message" in data
    assert "version" in data
    assert data["version"] == "0.1.0"


@pytest.mark.unit
def test_basic_health_check(client: TestClient):
    """Test basic health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"


@pytest.mark.integration
def test_api_health_check(client: TestClient):
    """Test API v1 health check endpoint."""
    response = client.get("/api/v1/health")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"
    assert data["environment"] in ["development", "production", "staging"]


@pytest.mark.integration
def test_database_health_check(client: TestClient):
    """Test database health check endpoint."""
    response = client.get("/api/v1/health/db")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "status" in data
    assert "connected" in data
    assert "message" in data
    
    # Database should be connected in tests
    assert data["connected"] is True
    assert data["status"] == "ok"


@pytest.mark.integration
def test_health_check_includes_request_id(client: TestClient):
    """Test that health check responses include request ID header."""
    response = client.get("/api/v1/health")
    
    assert "X-Request-ID" in response.headers
    request_id = response.headers["X-Request-ID"]
    assert len(request_id) > 0


@pytest.mark.integration
def test_health_check_includes_security_headers(client: TestClient):
    """Test that responses include security headers."""
    response = client.get("/api/v1/health")
    
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
