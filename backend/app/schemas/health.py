"""Health check schemas."""

from pydantic import BaseModel
from typing import Dict, Any


class HealthResponse(BaseModel):
    """Basic health check response."""
    status: str
    service: str
    version: str


class HealthCheckDetail(BaseModel):
    """Individual health check detail."""
    status: str
    error: str | None = None


class DetailedHealthResponse(BaseModel):
    """Detailed health check response."""
    status: str
    service: str
    version: str
    checks: Dict[str, HealthCheckDetail]