"""Cache management API endpoints."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
import logging

from app.core.cache import cache_manager
from app.services.cache_warming import cache_warming_service
from app.schemas.cache import (
    CacheStatsResponse,
    CacheWarmingRequest,
    CacheWarmingResponse,
    JurisdictionCacheStatsResponse,
    CacheInvalidationRequest,
    CacheInvalidationResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cache", tags=["cache"])


@router.get("/stats", response_model=CacheStatsResponse)
async def get_cache_stats():
    """Get overall cache statistics."""
    try:
        stats = await cache_manager.get_cache_stats()
        
        return CacheStatsResponse(
            status="success",
            stats=stats
        )
        
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/jurisdiction/{jurisdiction}", response_model=JurisdictionCacheStatsResponse)
async def get_jurisdiction_cache_stats(jurisdiction: str):
    """Get cache statistics for a specific jurisdiction."""
    try:
        if jurisdiction not in ["IN", "US"]:
            raise HTTPException(status_code=400, detail="Invalid jurisdiction. Must be 'IN' or 'US'")
        
        stats = await cache_manager.get_jurisdiction_cache_stats(jurisdiction)
        
        return JurisdictionCacheStatsResponse(
            status="success",
            jurisdiction=jurisdiction,
            stats=stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get jurisdiction cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/warm", response_model=CacheWarmingResponse)
async def warm_cache(
    request: CacheWarmingRequest,
    background_tasks: BackgroundTasks
):
    """Warm cache with frequently accessed data."""
    try:
        if request.background:
            # Start warming in background
            background_tasks.add_task(cache_warming_service.warm_all_caches)
            
            return CacheWarmingResponse(
                status="started",
                message="Cache warming started in background",
                background=True
            )
        else:
            # Warm cache synchronously
            result = await cache_warming_service.warm_all_caches()
            
            return CacheWarmingResponse(
                status=result.get("status", "completed"),
                message="Cache warming completed",
                background=False,
                results=result.get("results"),
                duration_seconds=result.get("duration_seconds")
            )
            
    except Exception as e:
        logger.error(f"Failed to warm cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/warming/status")
async def get_cache_warming_status():
    """Get current cache warming status."""
    try:
        status = await cache_warming_service.get_warming_status()
        return {"status": "success", "warming_status": status}
        
    except Exception as e:
        logger.error(f"Failed to get cache warming status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/warm/jurisdiction/{jurisdiction}")
async def warm_jurisdiction_cache(
    jurisdiction: str,
    document_types: Optional[List[str]] = None,
    analysis_types: Optional[List[str]] = None
):
    """Warm cache for a specific jurisdiction."""
    try:
        if jurisdiction not in ["IN", "US"]:
            raise HTTPException(status_code=400, detail="Invalid jurisdiction. Must be 'IN' or 'US'")
        
        doc_types = document_types or ["contract", "agreement", "mou", "nda"]
        analysis_types_list = analysis_types or ["comprehensive", "risk_analysis", "compliance_check"]
        
        result = await cache_manager.warm_jurisdiction_cache(
            jurisdiction, doc_types, analysis_types_list
        )
        
        return {
            "status": "success",
            "jurisdiction": jurisdiction,
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to warm jurisdiction cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invalidate", response_model=CacheInvalidationResponse)
async def invalidate_cache(request: CacheInvalidationRequest):
    """Invalidate cache entries based on criteria."""
    try:
        deleted_count = 0
        
        if request.document_id:
            # Invalidate document-specific cache
            deleted_count = await cache_manager.invalidate_document_analysis_cache(request.document_id)
            
        elif request.jurisdiction:
            # Invalidate jurisdiction-specific cache
            if request.jurisdiction not in ["IN", "US"]:
                raise HTTPException(status_code=400, detail="Invalid jurisdiction. Must be 'IN' or 'US'")
            
            deleted_count = await cache_manager.invalidate_jurisdiction_cache(request.jurisdiction)
            
        elif request.cache_pattern:
            # Invalidate by pattern (admin only - implement auth check)
            # This is a more dangerous operation, so it should be restricted
            raise HTTPException(status_code=403, detail="Pattern-based invalidation requires admin privileges")
            
        else:
            raise HTTPException(status_code=400, detail="Must specify document_id, jurisdiction, or cache_pattern")
        
        return CacheInvalidationResponse(
            status="success",
            deleted_count=deleted_count,
            message=f"Invalidated {deleted_count} cache entries"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to invalidate cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear/expired")
async def clear_expired_keys():
    """Clear expired cache keys."""
    try:
        cleared_count = await cache_manager.clear_expired_keys()
        
        return {
            "status": "success",
            "cleared_count": cleared_count,
            "message": f"Cleared {cleared_count} expired keys"
        }
        
    except Exception as e:
        logger.error(f"Failed to clear expired keys: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/warm/document/{document_id}")
async def warm_document_cache(
    document_id: str,
    document_type: str,
    jurisdiction: str
):
    """Warm cache for a specific document."""
    try:
        if jurisdiction not in ["IN", "US"]:
            raise HTTPException(status_code=400, detail="Invalid jurisdiction. Must be 'IN' or 'US'")
        
        result = await cache_warming_service.warm_document_specific_cache(
            document_id, document_type, jurisdiction
        )
        
        return {
            "status": "success",
            "document_id": document_id,
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to warm document cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def cache_health_check():
    """Check cache system health."""
    try:
        # Test Redis connection
        if not cache_manager.redis_client:
            return {
                "status": "unhealthy",
                "error": "Redis client not connected"
            }
        
        # Test basic operations
        test_key = "health_check_test"
        test_value = {"timestamp": "test"}
        
        # Test set
        set_success = await cache_manager.set(test_key, test_value, ttl=60)
        if not set_success:
            return {
                "status": "unhealthy",
                "error": "Failed to set test key"
            }
        
        # Test get
        retrieved_value = await cache_manager.get(test_key)
        if retrieved_value != test_value:
            return {
                "status": "unhealthy",
                "error": "Failed to retrieve test key"
            }
        
        # Test delete
        delete_success = await cache_manager.delete(test_key)
        if not delete_success:
            return {
                "status": "unhealthy",
                "error": "Failed to delete test key"
            }
        
        return {
            "status": "healthy",
            "message": "Cache system is functioning properly"
        }
        
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }