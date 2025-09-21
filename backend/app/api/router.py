"""Main API router configuration."""

from fastapi import APIRouter

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Import and include route modules
from .auth import router as auth_router
from .documents import router as documents_router
from .ai_analysis import router as ai_analysis_router
from .semantic_search import router as semantic_search_router
from .tasks import router as tasks_router
from .websocket import router as websocket_router
from .collaboration import router as collaboration_router
from .chat import router as chat_router
from .jurisdiction import router as jurisdiction_router
from .cache import router as cache_router
from .database import router as database_router

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])
api_router.include_router(ai_analysis_router, tags=["AI Analysis"])
api_router.include_router(semantic_search_router, tags=["Semantic Search"])
api_router.include_router(tasks_router, tags=["Task Management"])
api_router.include_router(websocket_router, tags=["WebSocket"])
api_router.include_router(collaboration_router, tags=["Collaboration"])
api_router.include_router(chat_router, tags=["Chat"])
api_router.include_router(jurisdiction_router, tags=["Jurisdiction"])
api_router.include_router(cache_router, tags=["Cache Management"])
api_router.include_router(database_router, tags=["Database Optimization"])


@api_router.get("/")
async def api_root():
    """API root endpoint."""
    return {
        "message": "LegalEase AI API v1",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }