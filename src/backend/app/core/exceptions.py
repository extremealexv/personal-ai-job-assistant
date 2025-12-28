"""Custom exception classes for API errors."""

from typing import Any, Optional


class APIException(Exception):
    """Base exception for all API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize API exception.

        Args:
            message: Human-readable error message
            status_code: HTTP status code
            detail: Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(message)


class NotFoundError(APIException):
    """Resource not found error (404)."""

    def __init__(
        self,
        resource: str,
        resource_id: Optional[str] = None,
        detail: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize not found error.

        Args:
            resource: Type of resource (e.g., "User", "Job Posting")
            resource_id: ID of the resource
            detail: Additional error details
        """
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with ID '{resource_id}' not found"
        super().__init__(message=message, status_code=404, detail=detail)


class UnauthorizedError(APIException):
    """Authentication required error (401)."""

    def __init__(
        self,
        message: str = "Authentication required",
        detail: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize unauthorized error."""
        super().__init__(message=message, status_code=401, detail=detail)


class ForbiddenError(APIException):
    """Permission denied error (403)."""

    def __init__(
        self,
        message: str = "Permission denied",
        detail: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize forbidden error."""
        super().__init__(message=message, status_code=403, detail=detail)


class ValidationError(APIException):
    """Request validation error (422)."""

    def __init__(
        self,
        message: str = "Validation error",
        errors: Optional[list[dict[str, Any]]] = None,
        detail: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize validation error.

        Args:
            message: Error message
            errors: List of validation errors
            detail: Additional error details
        """
        detail = detail or {}
        if errors:
            detail["errors"] = errors
        super().__init__(message=message, status_code=422, detail=detail)


class ConflictError(APIException):
    """Resource conflict error (409)."""

    def __init__(
        self,
        message: str = "Resource conflict",
        detail: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize conflict error."""
        super().__init__(message=message, status_code=409, detail=detail)


class DatabaseError(APIException):
    """Database operation error (500)."""

    def __init__(
        self,
        message: str = "Database error",
        detail: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize database error."""
        super().__init__(message=message, status_code=500, detail=detail)


class ExternalServiceError(APIException):
    """External service error (502/503)."""

    def __init__(
        self,
        service: str,
        message: Optional[str] = None,
        status_code: int = 503,
        detail: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize external service error.

        Args:
            service: Name of the external service
            message: Error message
            status_code: HTTP status code (502 or 503)
            detail: Additional error details
        """
        message = message or f"{service} service unavailable"
        detail = detail or {}
        detail["service"] = service
        super().__init__(message=message, status_code=status_code, detail=detail)


class RateLimitError(APIException):
    """Rate limit exceeded error (429)."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        detail: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Seconds until retry is allowed
            detail: Additional error details
        """
        detail = detail or {}
        if retry_after:
            detail["retry_after"] = retry_after
        super().__init__(message=message, status_code=429, detail=detail)
