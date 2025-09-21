"""Main FastAPI application entry point."""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging
import asyncio

from app.config import settings
from app.database import init_db, close_db, get_db
from app.api import api_router
from app.schemas.health import HealthResponse, DetailedHealthResponse, HealthCheckDetail
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.middleware.security import (
    SecurityMiddleware,
    RequestValidationMiddleware,
    SQLInjectionProtectionMiddleware,
    FileUploadSecurityMiddleware
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting LegalEase AI Backend...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
        
        # Initialize cache manager
        from app.core.cache import cache_manager
        await cache_manager.connect()
        logger.info("Cache manager connected successfully")
        
        # Start cache warming in background (non-blocking)
        if not settings.debug:  # Only in production
            from app.services.cache_warming import cache_warming_service
            asyncio.create_task(cache_warming_service.warm_all_caches())
            logger.info("Cache warming started in background")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down LegalEase AI Backend...")
    try:
        # Disconnect cache manager
        from app.core.cache import cache_manager
        await cache_manager.disconnect()
        logger.info("Cache manager disconnected")
        
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="LegalEase AI API",
    description="Legal document analysis platform with multi-jurisdiction support",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add security middleware (order matters - most specific first)
app.add_middleware(FileUploadSecurityMiddleware)
app.add_middleware(SQLInjectionProtectionMiddleware)
app.add_middleware(RequestValidationMiddleware)
app.add_middleware(SecurityMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include API router
app.include_router(api_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "LegalEase AI API", "version": "0.1.0"}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy", 
        service="legalease-ai-backend",
        version="0.1.0"
    )


@app.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check with database connectivity."""
    overall_status = "healthy"
    checks = {}
    
    # Check database connectivity
    try:
        result = await db.execute(text("SELECT 1"))
        result.fetchone()
        checks["database"] = HealthCheckDetail(status="healthy")
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        overall_status = "unhealthy"
        checks["database"] = HealthCheckDetail(
            status="unhealthy",
            error=str(e)
        )
    
    return DetailedHealthResponse(
        status=overall_status,
        service="legalease-ai-backend",
        version="0.1.0",
        checks=checks
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.reload,
    )