"""Main API router configuration."""

from fastapi import APIRouter

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Import and include route modules
from .auth import router as auth_router
from .documents import router as documents_router
# from .analysis import router as analysis_router

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])
# api_router.include_router(analysis_router, prefix="/analysis", tags=["analysis"])


@api_router.get("/")
async def api_root():
    """API root endpoint."""
    return {
        "message": "LegalEase AI API v1",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }