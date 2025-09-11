"""Base Pydantic schemas."""

from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response schema."""
    message: str
    timestamp: str = datetime.utcnow().isoformat()


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
    timestamp: str = datetime.utcnow().isoformat()


class PaginatedResponse(BaseModel):
    """Paginated response schema."""
    items: list[Any]
    total: int
    page: int
    size: int
    pages: int