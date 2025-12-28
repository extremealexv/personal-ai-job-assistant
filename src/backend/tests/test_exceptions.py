"""Tests for custom exception handling."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.core.exceptions import (
    APIException,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from app.main import app


@pytest.mark.unit
def test_not_found_error():
    """Test NotFoundError exception."""
    error = NotFoundError(resource="User", resource_id="123")
    
    assert error.status_code == 404
    assert "User with ID '123' not found" in error.message


@pytest.mark.unit
def test_unauthorized_error():
    """Test UnauthorizedError exception."""
    error = UnauthorizedError()
    
    assert error.status_code == 401
    assert "Authentication required" in error.message


@pytest.mark.unit
def test_forbidden_error():
    """Test ForbiddenError exception."""
    error = ForbiddenError()
    
    assert error.status_code == 403
    assert "Permission denied" in error.message


@pytest.mark.unit
def test_validation_error():
    """Test ValidationError exception."""
    errors = [{"field": "email", "message": "Invalid email format"}]
    error = ValidationError(errors=errors)
    
    assert error.status_code == 422
    assert "errors" in error.detail
    assert error.detail["errors"] == errors


@pytest.mark.unit
def test_conflict_error():
    """Test ConflictError exception."""
    error = ConflictError(message="Email already exists")
    
    assert error.status_code == 409
    assert "Email already exists" in error.message


@pytest.mark.integration
def test_validation_error_response_format(client: TestClient):
    """Test validation error response format from API."""
    # Create endpoint that will trigger validation error
    from pydantic import BaseModel, Field
    
    class TestModel(BaseModel):
        email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    
    @app.post("/test-validation")
    async def test_endpoint(data: TestModel):
        return {"success": True}
    
    # Send invalid data
    response = client.post("/test-validation", json={"email": "invalid-email"})
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    
    assert "error" in data
    assert "message" in data["error"]
    assert "status_code" in data["error"]
    assert data["error"]["status_code"] == 422


@pytest.mark.integration
def test_error_includes_request_id(client: TestClient):
    """Test that error responses include request ID."""
    # Trigger a validation error
    from pydantic import BaseModel
    
    class TestModel(BaseModel):
        required_field: str
    
    @app.post("/test-error")
    async def test_endpoint(data: TestModel):
        return {"success": True}
    
    response = client.post("/test-error", json={})
    
    assert "X-Request-ID" in response.headers
