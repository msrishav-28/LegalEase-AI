"""Custom exceptions and exception handlers."""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Union

from app.schemas.base import ErrorResponse

logger = logging.getLogger(__name__)


class LegalEaseException(Exception):
    """Base exception for LegalEase AI application."""
    
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class DatabaseException(LegalEaseException):
    """Database-related exceptions."""
    pass


class AuthenticationException(LegalEaseException):
    """Authentication-related exceptions."""
    pass


class DocumentProcessingException(LegalEaseException):
    """Document processing exceptions."""
    pass


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    logger.error(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            code=f"HTTP_{exc.status_code}"
        ).model_dump()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation exceptions."""
    logger.error(f"Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="Validation error",
            detail=str(exc.errors()),
            code="VALIDATION_ERROR"
        ).model_dump()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {type(exc).__name__} - {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred",
            code="INTERNAL_ERROR"
        ).model_dump()
    )