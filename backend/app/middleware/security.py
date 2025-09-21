"""Security middleware for FastAPI application."""

import time
import logging
from typing import Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.security import rate_limiter, SecurityHeaders, InputValidator
from app.schemas.base import ErrorResponse

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.security_headers = SecurityHeaders()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through security checks."""
        start_time = time.time()
        
        try:
            # Get client IP
            client_ip = self._get_client_ip(request)
            
            # Rate limiting check
            if not await rate_limiter.is_allowed(client_ip, request.url.path):
                logger.warning(f"Rate limit exceeded for IP {client_ip} on {request.url.path}")
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content=ErrorResponse(
                        error="Rate limit exceeded",
                        detail="Too many requests. Please try again later.",
                        code="RATE_LIMIT_EXCEEDED"
                    ).model_dump()
                )
            
            # Input validation for query parameters
            await self._validate_query_params(request)
            
            # Content-Length validation
            if request.headers.get("content-length"):
                content_length = int(request.headers["content-length"])
                if content_length > 100 * 1024 * 1024:  # 100MB limit
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content=ErrorResponse(
                            error="Request too large",
                            detail="Request body exceeds maximum size limit",
                            code="REQUEST_TOO_LARGE"
                        ).model_dump()
                    )
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            for header, value in self.security_headers.get_security_headers().items():
                response.headers[header] = value
            
            # Add processing time header
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log request
            logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s - "
                f"IP: {client_ip}"
            )
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Internal server error",
                    detail="An unexpected error occurred",
                    code="INTERNAL_ERROR"
                ).model_dump()
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers (when behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
    
    async def _validate_query_params(self, request: Request):
        """Validate query parameters for security issues."""
        for key, value in request.query_params.items():
            try:
                # Validate parameter name
                InputValidator.validate_string(key, max_length=100)
                
                # Validate parameter value
                if isinstance(value, str):
                    InputValidator.validate_string(value, max_length=1000)
                    
            except ValueError as e:
                logger.warning(f"Invalid query parameter {key}={value}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid query parameter: {str(e)}"
                )


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Request validation middleware."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Validate request structure and content."""
        try:
            # Validate HTTP method
            allowed_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"}
            if request.method not in allowed_methods:
                return JSONResponse(
                    status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                    content=ErrorResponse(
                        error="Method not allowed",
                        detail=f"HTTP method {request.method} is not allowed",
                        code="METHOD_NOT_ALLOWED"
                    ).model_dump()
                )
            
            # Validate Content-Type for POST/PUT/PATCH requests
            if request.method in {"POST", "PUT", "PATCH"}:
                content_type = request.headers.get("content-type", "")
                
                # Allow multipart/form-data for file uploads
                if not (
                    content_type.startswith("application/json") or
                    content_type.startswith("multipart/form-data") or
                    content_type.startswith("application/x-www-form-urlencoded")
                ):
                    return JSONResponse(
                        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        content=ErrorResponse(
                            error="Unsupported media type",
                            detail=f"Content-Type {content_type} is not supported",
                            code="UNSUPPORTED_MEDIA_TYPE"
                        ).model_dump()
                    )
            
            # Validate User-Agent (basic bot detection)
            user_agent = request.headers.get("user-agent", "")
            if not user_agent or len(user_agent) < 10:
                logger.warning(f"Suspicious request with minimal User-Agent: {user_agent}")
            
            return await call_next(request)
            
        except Exception as e:
            logger.error(f"Request validation error: {e}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ErrorResponse(
                    error="Invalid request",
                    detail="Request validation failed",
                    code="INVALID_REQUEST"
                ).model_dump()
            )


class SQLInjectionProtectionMiddleware(BaseHTTPMiddleware):
    """SQL injection protection middleware."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check for SQL injection patterns in request."""
        try:
            # Check URL path
            path = str(request.url.path)
            if self._contains_sql_injection(path):
                logger.warning(f"SQL injection attempt detected in path: {path}")
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(
                        error="Invalid request",
                        detail="Request contains potentially malicious content",
                        code="MALICIOUS_REQUEST"
                    ).model_dump()
                )
            
            # Check query parameters
            for key, value in request.query_params.items():
                if self._contains_sql_injection(f"{key}={value}"):
                    logger.warning(f"SQL injection attempt detected in query: {key}={value}")
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content=ErrorResponse(
                            error="Invalid request",
                            detail="Request contains potentially malicious content",
                            code="MALICIOUS_REQUEST"
                        ).model_dump()
                    )
            
            return await call_next(request)
            
        except Exception as e:
            logger.error(f"SQL injection protection error: {e}")
            return await call_next(request)
    
    def _contains_sql_injection(self, text: str) -> bool:
        """Check if text contains SQL injection patterns."""
        from app.core.security import SecurityConfig
        
        text_lower = text.lower()
        for pattern in SecurityConfig.SQL_INJECTION_PATTERNS:
            import re
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False


class FileUploadSecurityMiddleware(BaseHTTPMiddleware):
    """File upload security middleware."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Validate file uploads for security."""
        try:
            # Only process multipart/form-data requests
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith("multipart/form-data"):
                return await call_next(request)
            
            # Check if this is a file upload endpoint
            if "/upload" not in request.url.path:
                return await call_next(request)
            
            # Additional file upload validations will be handled in the endpoint
            # This middleware focuses on request-level security
            
            return await call_next(request)
            
        except Exception as e:
            logger.error(f"File upload security error: {e}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ErrorResponse(
                    error="File upload error",
                    detail="File upload validation failed",
                    code="FILE_UPLOAD_ERROR"
                ).model_dump()
            )