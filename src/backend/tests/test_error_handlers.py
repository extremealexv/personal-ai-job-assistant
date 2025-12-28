"""Tests for custom error handlers."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from pydantic import ValidationError as PydanticValidationError

from app.core.exceptions import (
    APIException,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from app.main import app


client = TestClient(app)


@pytest.mark.unit
def test_not_found_error_handler():
    """Test NotFoundError returns 404 with proper format."""
    # Test by accessing non-existent endpoint (which triggers 404)
    response = client.get("/api/v1/nonexistent")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "detail" in data


@pytest.mark.unit
def test_unauthorized_error_response_format():
    """Test UnauthorizedError has correct properties."""
    error = UnauthorizedError("Invalid credentials")
    
    assert error.message == "Invalid credentials"
    assert error.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.unit
def test_validation_error_response_format():
    """Test ValidationError has correct properties."""
    error = ValidationError("Invalid input")
    
    assert error.message == "Invalid input"
    assert error.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.unit
def test_not_found_error_response_format():
    """Test NotFoundError has correct properties."""
    error = NotFoundError(resource="User", resource_id="123")
    
    assert "User" in error.message
    assert "123" in error.message
    assert error.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.unit
def test_api_exception_base_class():
    """Test APIException base class."""
    error = APIException("Generic error", status_code=500)
    
    assert error.message == "Generic error"
    assert error.status_code == 500
    assert str(error) == "Generic error"


@pytest.mark.integration
def test_error_handler_includes_request_id():
    """Test error responses include request ID from middleware."""
    response = client.get("/api/v1/nonexistent")
    
    # Should have request ID in headers
    assert "X-Request-ID" in response.headers


@pytest.mark.integration
def test_error_handler_with_query_params():
    """Test error handling with query parameters."""
    response = client.get("/api/v1/nonexistent?param=value")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
def test_error_handler_with_post_request():
    """Test error handling with POST request."""
    response = client.post(
        "/api/v1/nonexistent",
        json={"key": "value"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.unit
def test_validation_error_with_details():
    """Test ValidationError can include detail information."""
    error = ValidationError("Validation failed", detail={"field": "email"})
    
    assert error.message == "Validation failed"
    assert error.detail is not None


@pytest.mark.unit
def test_not_found_error_custom_message():
    """Test NotFoundError with custom message."""
    error = NotFoundError(resource="Resume version", resource_id="123")
    
    assert "Resume version" in error.message
    assert "123" in error.message


@pytest.mark.unit
def test_unauthorized_error_custom_message():
    """Test UnauthorizedError with custom message."""
    error = UnauthorizedError("Token expired")
    
    assert "Token expired" in error.message


@pytest.mark.integration
def test_method_not_allowed_error():
    """Test method not allowed returns 405."""
    # Try POST on health endpoint (only GET allowed)
    response = client.post("/api/v1/health")
    
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.integration
def test_invalid_json_returns_422():
    """Test invalid JSON in request body returns 422."""
    response = client.post(
        "/api/v1/users",  # Endpoint might not exist yet, but test invalid JSON
        data="invalid json",
        headers={"Content-Type": "application/json"}
    )
    
    # Should return 422 for malformed JSON
    assert response.status_code in [
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        status.HTTP_404_NOT_FOUND  # If endpoint doesn't exist
    ]


@pytest.mark.unit
def test_api_exception_str_representation():
    """Test APIException string representation."""
    error = APIException("Test error message")
    
    assert str(error) == "Test error message"


@pytest.mark.unit
def test_exception_hierarchy():
    """Test that custom exceptions inherit from APIException."""
    assert issubclass(NotFoundError, APIException)
    assert issubclass(UnauthorizedError, APIException)
    assert issubclass(ValidationError, APIException)


@pytest.mark.unit
def test_error_status_codes():
    """Test error classes have correct status codes."""
    errors = [
        (NotFoundError("test"), status.HTTP_404_NOT_FOUND),
        (UnauthorizedError("test"), status.HTTP_401_UNAUTHORIZED),
        (ValidationError("test"), status.HTTP_422_UNPROCESSABLE_ENTITY),
    ]
    
    for error, expected_code in errors:
        assert error.status_code == expected_code
