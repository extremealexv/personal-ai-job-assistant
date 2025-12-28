"""Exception handlers for API errors."""

import logging
from typing import Union

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions import APIException

logger = logging.getLogger(__name__)


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle custom API exceptions.

    Args:
        request: FastAPI request object
        exc: API exception instance

    Returns:
        JSON response with error details
    """
    logger.error(
        f"API Exception: {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "detail": exc.detail,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "status_code": exc.status_code,
                "detail": exc.detail,
            }
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: Union[RequestValidationError, PydanticValidationError],
) -> JSONResponse:
    """Handle Pydantic validation errors.

    Args:
        request: FastAPI request object
        exc: Validation error instance

    Returns:
        JSON response with validation errors
    """
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    logger.warning(
        f"Validation error on {request.method} {request.url.path}",
        extra={"errors": errors},
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "message": "Validation error",
                "status_code": 422,
                "detail": {"errors": errors},
            }
        },
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Handle SQLAlchemy integrity errors (unique constraints, foreign keys, etc.).

    Args:
        request: FastAPI request object
        exc: Integrity error instance

    Returns:
        JSON response with error details
    """
    logger.error(
        f"Database integrity error on {request.method} {request.url.path}",
        extra={"error": str(exc.orig)},
    )

    # Parse common constraint violations
    error_msg = str(exc.orig)
    if "UNIQUE constraint" in error_msg or "duplicate key" in error_msg:
        message = "Resource already exists"
        status_code = status.HTTP_409_CONFLICT
    elif "FOREIGN KEY constraint" in error_msg or "foreign key" in error_msg.lower():
        message = "Referenced resource does not exist"
        status_code = status.HTTP_400_BAD_REQUEST
    else:
        message = "Database constraint violation"
        status_code = status.HTTP_400_BAD_REQUEST

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "message": message,
                "status_code": status_code,
                "detail": {"database_error": error_msg},
            }
        },
    )


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle general SQLAlchemy errors.

    Args:
        request: FastAPI request object
        exc: SQLAlchemy error instance

    Returns:
        JSON response with error details
    """
    logger.error(
        f"Database error on {request.method} {request.url.path}",
        extra={"error": str(exc)},
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "Database error occurred",
                "status_code": 500,
                "detail": {},
            }
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions.

    Args:
        request: FastAPI request object
        exc: Exception instance

    Returns:
        JSON response with error details
    """
    logger.error(
        f"Unexpected error on {request.method} {request.url.path}",
        exc_info=True,
    )

    # In production, don't expose internal error details
    from app.config import settings

    detail = {"error_type": type(exc).__name__}
    if settings.debug:
        detail["error_message"] = str(exc)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "Internal server error",
                "status_code": 500,
                "detail": detail,
            }
        },
    )
