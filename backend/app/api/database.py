"""Database optimization and monitoring API endpoints."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
import logging

from app.services.database_optimization import db_optimization_service
from app.schemas.database import (
    DatabaseStatsResponse,
    IndexCreationResponse,
    QueryPerformanceRequest,
    QueryPerformanceResponse,
    SlowQueriesResponse,
    ConnectionPoolStatsResponse,
    DatabaseOptimizationRequest,
    DatabaseOptimizationResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/database", tags=["database"])


@router.post("/indexes/create", response_model=IndexCreationResponse)
async def create_jurisdiction_indexes(background_tasks: BackgroundTasks):
    """Create jurisdiction-specific database indexes for optimal performance."""
    try:
        # Run index creation in background to avoid timeout
        background_tasks.add_task(db_optimization_service.create_jurisdiction_indexes)
        
        return IndexCreationResponse(
            status="started",
            message="Index creation started in background"
        )
        
    except Exception as e:
        logger.error(f"Failed to start index creation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=DatabaseStatsResponse)
async def get_database_stats():
    """Get comprehensive database statistics."""
    try:
        # Get database size info
        size_info = await db_optimization_service.get_database_size_info()
        
        # Get connection pool stats
        pool_stats = await db_optimization_service.get_connection_pool_stats()
        
        # Get index usage stats
        index_stats = await db_optimization_service.check_index_usage()
        
        return DatabaseStatsResponse(
            status="success",
            database_size=size_info.get("database_size"),
            table_sizes=size_info.get("table_sizes", []),
            connection_pool=pool_stats.get("stats", {}),
            index_usage=index_stats.get("index_stats", [])
        )
        
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/analyze", response_model=QueryPerformanceResponse)
async def analyze_query_performance(request: QueryPerformanceRequest):
    """Analyze query performance using EXPLAIN ANALYZE."""
    try:
        result = await db_optimization_service.analyze_query_performance(
            request.query, request.params
        )
        
        if result["status"] == "failed":
            raise HTTPException(status_code=400, detail=result["error"])
        
        return QueryPerformanceResponse(
            status="success",
            metrics=result["metrics"],
            execution_plan=result.get("full_plan")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze query performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queries/slow", response_model=SlowQueriesResponse)
async def get_slow_queries(limit: int = 10):
    """Get slow queries from database statistics."""
    try:
        if limit > 100:
            raise HTTPException(status_code=400, detail="Limit cannot exceed 100")
        
        result = await db_optimization_service.get_slow_queries(limit)
        
        return SlowQueriesResponse(
            status=result["status"],
            queries=result.get("queries", []),
            total_count=len(result.get("queries", []))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get slow queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connection-pool", response_model=ConnectionPoolStatsResponse)
async def get_connection_pool_stats():
    """Get connection pool statistics."""
    try:
        result = await db_optimization_service.get_connection_pool_stats()
        
        if result["status"] == "failed":
            raise HTTPException(status_code=500, detail=result["error"])
        
        return ConnectionPoolStatsResponse(
            status="success",
            stats=result["stats"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get connection pool stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize", response_model=DatabaseOptimizationResponse)
async def optimize_database(
    request: DatabaseOptimizationRequest,
    background_tasks: BackgroundTasks
):
    """Perform database optimization operations."""
    try:
        results = {}
        
        if request.update_statistics:
            if request.background:
                background_tasks.add_task(db_optimization_service.optimize_table_statistics)
                results["statistics"] = "started_in_background"
            else:
                stats_result = await db_optimization_service.optimize_table_statistics()
                results["statistics"] = stats_result
        
        if request.vacuum_analyze:
            if request.background:
                background_tasks.add_task(db_optimization_service.vacuum_analyze_tables)
                results["vacuum_analyze"] = "started_in_background"
            else:
                vacuum_result = await db_optimization_service.vacuum_analyze_tables()
                results["vacuum_analyze"] = vacuum_result
        
        if request.create_indexes:
            if request.background:
                background_tasks.add_task(db_optimization_service.create_jurisdiction_indexes)
                results["indexes"] = "started_in_background"
            else:
                index_result = await db_optimization_service.create_jurisdiction_indexes()
                results["indexes"] = index_result
        
        return DatabaseOptimizationResponse(
            status="completed" if not request.background else "started",
            operations=results,
            background=request.background
        )
        
    except Exception as e:
        logger.error(f"Failed to optimize database: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/indexes/usage")
async def get_index_usage_stats():
    """Get index usage statistics."""
    try:
        result = await db_optimization_service.check_index_usage()
        
        if result["status"] == "failed":
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "status": "success",
            "index_stats": result["index_stats"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get index usage stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query-stats")
async def get_query_statistics():
    """Get query performance statistics."""
    try:
        result = await db_optimization_service.get_query_statistics()
        return result
        
    except Exception as e:
        logger.error(f"Failed to get query statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/maintenance/vacuum")
async def vacuum_analyze_tables(background_tasks: BackgroundTasks):
    """Perform VACUUM ANALYZE on all tables."""
    try:
        background_tasks.add_task(db_optimization_service.vacuum_analyze_tables)
        
        return {
            "status": "started",
            "message": "VACUUM ANALYZE started in background"
        }
        
    except Exception as e:
        logger.error(f"Failed to start VACUUM ANALYZE: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/maintenance/statistics")
async def update_table_statistics(background_tasks: BackgroundTasks):
    """Update table statistics for better query planning."""
    try:
        background_tasks.add_task(db_optimization_service.optimize_table_statistics)
        
        return {
            "status": "started", 
            "message": "Statistics update started in background"
        }
        
    except Exception as e:
        logger.error(f"Failed to start statistics update: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def database_health_check():
    """Check database system health."""
    try:
        # Get connection pool stats
        pool_result = await db_optimization_service.get_connection_pool_stats()
        
        # Get database size (basic connectivity test)
        size_result = await db_optimization_service.get_database_size_info()
        
        health_status = "healthy"
        issues = []
        
        # Check connection pool utilization
        if pool_result["status"] == "success":
            utilization = pool_result["stats"].get("utilization_percent", 0)
            if utilization > 80:
                issues.append(f"High connection pool utilization: {utilization:.1f}%")
                health_status = "warning"
        else:
            issues.append("Failed to get connection pool stats")
            health_status = "unhealthy"
        
        # Check database connectivity
        if size_result["status"] != "success":
            issues.append("Database connectivity issues")
            health_status = "unhealthy"
        
        return {
            "status": health_status,
            "issues": issues,
            "connection_pool": pool_result.get("stats", {}),
            "database_accessible": size_result["status"] == "success"
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }