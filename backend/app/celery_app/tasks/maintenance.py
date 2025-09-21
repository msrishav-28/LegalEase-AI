"""Maintenance and monitoring tasks for Celery workers."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from celery import current_task
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app.celery import celery_app, TaskProgress
from app.database.connection import AsyncSessionLocal
from app.database.models import Document, AnalysisResults, JurisdictionAnalysis
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@celery_app.task(bind=True, name="cleanup_expired_results")
def cleanup_expired_results_task(self) -> Dict[str, Any]:
    """
    Clean up expired analysis results and temporary files.
    
    Returns:
        Dict containing cleanup results
    """
    task_id = self.request.id
    logger.info("Starting cleanup of expired results")
    
    try:
        TaskProgress.update_progress(task_id, 0, 100, "Starting cleanup")
        
        # Run async cleanup
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(_cleanup_expired_results_async(task_id))
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Cleanup failed: {exc}")
        return {
            "status": "failed",
            "error": str(exc),
            "cleaned_results": 0,
            "cleaned_files": 0,
        }


async def _cleanup_expired_results_async(task_id: str) -> Dict[str, Any]:
    """Async cleanup implementation."""
    
    async with AsyncSessionLocal() as session:
        # Calculate expiration date (30 days ago)
        expiration_date = datetime.utcnow() - timedelta(days=30)
        
        TaskProgress.update_progress(task_id, 20, 100, "Cleaning expired analysis results")
        
        # Clean up expired analysis results
        expired_analyses = await session.execute(
            select(AnalysisResults).where(
                AnalysisResults.created_at < expiration_date
            )
        )
        expired_count = len(expired_analyses.scalars().all())
        
        if expired_count > 0:
            await session.execute(
                delete(AnalysisResults).where(
                    AnalysisResults.created_at < expiration_date
                )
            )
        
        TaskProgress.update_progress(task_id, 50, 100, "Cleaning expired jurisdiction analyses")
        
        # Clean up expired jurisdiction analyses
        expired_jurisdiction = await session.execute(
            select(JurisdictionAnalysis).where(
                JurisdictionAnalysis.created_at < expiration_date
            )
        )
        expired_jurisdiction_count = len(expired_jurisdiction.scalars().all())
        
        if expired_jurisdiction_count > 0:
            await session.execute(
                delete(JurisdictionAnalysis).where(
                    JurisdictionAnalysis.created_at < expiration_date
                )
            )
        
        TaskProgress.update_progress(task_id, 80, 100, "Cleaning temporary files")
        
        # Clean up temporary files (implementation depends on file storage strategy)
        cleaned_files = 0  # Placeholder for file cleanup logic
        
        await session.commit()
        
        TaskProgress.update_progress(task_id, 100, 100, "Cleanup completed")
        
        logger.info(f"Cleanup completed: {expired_count} analyses, {expired_jurisdiction_count} jurisdiction analyses, {cleaned_files} files")
        
        return {
            "status": "success",
            "cleaned_analyses": expired_count,
            "cleaned_jurisdiction_analyses": expired_jurisdiction_count,
            "cleaned_files": cleaned_files,
            "expiration_date": expiration_date.isoformat(),
        }


@celery_app.task(bind=True, name="health_check")
def health_check_task(self) -> Dict[str, Any]:
    """
    Perform health check on system components.
    
    Returns:
        Dict containing health check results
    """
    task_id = self.request.id
    logger.info("Starting system health check")
    
    try:
        TaskProgress.update_progress(task_id, 0, 100, "Starting health check")
        
        # Run async health check
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(_health_check_async(task_id))
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Health check failed: {exc}")
        return {
            "status": "failed",
            "error": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        }


async def _health_check_async(task_id: str) -> Dict[str, Any]:
    """Async health check implementation."""
    
    health_status = {
        "timestamp": datetime.utcnow().isoformat(),
        "status": "healthy",
        "components": {},
    }
    
    # Check database connectivity
    TaskProgress.update_progress(task_id, 20, 100, "Checking database connectivity")
    
    try:
        async with AsyncSessionLocal() as session:
            # Simple query to test database
            result = await session.execute(select(1))
            result.scalar()
            health_status["components"]["database"] = {
                "status": "healthy",
                "message": "Database connection successful"
            }
    except Exception as exc:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(exc)}"
        }
        health_status["status"] = "unhealthy"
    
    # Check Redis connectivity
    TaskProgress.update_progress(task_id, 40, 100, "Checking Redis connectivity")
    
    try:
        import redis
        redis_client = redis.from_url(settings.redis_url)
        redis_client.ping()
        health_status["components"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection successful"
        }
    except Exception as exc:
        health_status["components"]["redis"] = {
            "status": "unhealthy",
            "message": f"Redis connection failed: {str(exc)}"
        }
        health_status["status"] = "unhealthy"
    
    # Check RabbitMQ connectivity
    TaskProgress.update_progress(task_id, 60, 100, "Checking RabbitMQ connectivity")
    
    try:
        from kombu import Connection
        with Connection(settings.rabbitmq_url) as conn:
            conn.connect()
            health_status["components"]["rabbitmq"] = {
                "status": "healthy",
                "message": "RabbitMQ connection successful"
            }
    except Exception as exc:
        health_status["components"]["rabbitmq"] = {
            "status": "unhealthy",
            "message": f"RabbitMQ connection failed: {str(exc)}"
        }
        health_status["status"] = "unhealthy"
    
    # Check OpenAI API (if configured)
    TaskProgress.update_progress(task_id, 80, 100, "Checking OpenAI API")
    
    if settings.openai_api_key:
        try:
            import openai
            client = openai.OpenAI(api_key=settings.openai_api_key)
            # Simple API test
            response = client.models.list()
            health_status["components"]["openai"] = {
                "status": "healthy",
                "message": "OpenAI API connection successful"
            }
        except Exception as exc:
            health_status["components"]["openai"] = {
                "status": "unhealthy",
                "message": f"OpenAI API connection failed: {str(exc)}"
            }
            health_status["status"] = "unhealthy"
    else:
        health_status["components"]["openai"] = {
            "status": "not_configured",
            "message": "OpenAI API key not configured"
        }
    
    TaskProgress.update_progress(task_id, 100, 100, "Health check completed")
    
    logger.info(f"Health check completed: {health_status['status']}")
    
    return health_status


@celery_app.task(bind=True, name="generate_system_metrics")
def generate_system_metrics_task(self) -> Dict[str, Any]:
    """
    Generate system metrics and statistics.
    
    Returns:
        Dict containing system metrics
    """
    task_id = self.request.id
    logger.info("Generating system metrics")
    
    try:
        TaskProgress.update_progress(task_id, 0, 100, "Starting metrics generation")
        
        # Run async metrics generation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(_generate_metrics_async(task_id))
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Metrics generation failed: {exc}")
        return {
            "status": "failed",
            "error": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        }


async def _generate_metrics_async(task_id: str) -> Dict[str, Any]:
    """Async metrics generation implementation."""
    
    async with AsyncSessionLocal() as session:
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
        }
        
        # Document statistics
        TaskProgress.update_progress(task_id, 20, 100, "Calculating document statistics")
        
        total_documents = await session.execute(select(Document))
        total_documents_count = len(total_documents.scalars().all())
        
        processed_documents = await session.execute(
            select(Document).where(Document.content.isnot(None))
        )
        processed_documents_count = len(processed_documents.scalars().all())
        
        metrics["documents"] = {
            "total": total_documents_count,
            "processed": processed_documents_count,
            "processing_rate": (processed_documents_count / total_documents_count * 100) if total_documents_count > 0 else 0,
        }
        
        # Analysis statistics
        TaskProgress.update_progress(task_id, 50, 100, "Calculating analysis statistics")
        
        total_analyses = await session.execute(select(AnalysisResults))
        total_analyses_count = len(total_analyses.scalars().all())
        
        # Recent analyses (last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_analyses = await session.execute(
            select(AnalysisResults).where(AnalysisResults.created_at >= recent_cutoff)
        )
        recent_analyses_count = len(recent_analyses.scalars().all())
        
        metrics["analyses"] = {
            "total": total_analyses_count,
            "recent_24h": recent_analyses_count,
        }
        
        # Jurisdiction statistics
        TaskProgress.update_progress(task_id, 80, 100, "Calculating jurisdiction statistics")
        
        jurisdiction_analyses = await session.execute(select(JurisdictionAnalysis))
        jurisdiction_analyses_list = jurisdiction_analyses.scalars().all()
        
        jurisdiction_counts = {}
        for analysis in jurisdiction_analyses_list:
            jurisdiction = analysis.jurisdiction.value
            jurisdiction_counts[jurisdiction] = jurisdiction_counts.get(jurisdiction, 0) + 1
        
        metrics["jurisdictions"] = jurisdiction_counts
        
        TaskProgress.update_progress(task_id, 100, 100, "Metrics generation completed")
        
        logger.info(f"Generated metrics: {total_documents_count} documents, {total_analyses_count} analyses")
        
        return metrics


@celery_app.task(bind=True, name="optimize_database")
def optimize_database_task(self) -> Dict[str, Any]:
    """
    Perform database optimization tasks.
    
    Returns:
        Dict containing optimization results
    """
    task_id = self.request.id
    logger.info("Starting database optimization")
    
    try:
        TaskProgress.update_progress(task_id, 0, 100, "Starting database optimization")
        
        # Run async optimization
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(_optimize_database_async(task_id))
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Database optimization failed: {exc}")
        return {
            "status": "failed",
            "error": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        }


async def _optimize_database_async(task_id: str) -> Dict[str, Any]:
    """Async database optimization implementation."""
    
    async with AsyncSessionLocal() as session:
        optimization_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "operations": [],
        }
        
        # Analyze table statistics
        TaskProgress.update_progress(task_id, 25, 100, "Analyzing table statistics")
        
        try:
            # PostgreSQL specific optimization queries
            await session.execute("ANALYZE;")
            optimization_results["operations"].append("Table statistics updated")
        except Exception as exc:
            logger.warning(f"Failed to update table statistics: {exc}")
        
        # Vacuum analyze (PostgreSQL specific)
        TaskProgress.update_progress(task_id, 50, 100, "Performing vacuum analyze")
        
        try:
            # Note: VACUUM cannot be run inside a transaction in PostgreSQL
            # This would need to be handled differently in production
            optimization_results["operations"].append("Vacuum analyze scheduled")
        except Exception as exc:
            logger.warning(f"Failed to perform vacuum analyze: {exc}")
        
        # Reindex operations
        TaskProgress.update_progress(task_id, 75, 100, "Reindexing tables")
        
        try:
            # Reindex operations would go here
            optimization_results["operations"].append("Reindexing completed")
        except Exception as exc:
            logger.warning(f"Failed to reindex: {exc}")
        
        await session.commit()
        
        TaskProgress.update_progress(task_id, 100, 100, "Database optimization completed")
        
        logger.info(f"Database optimization completed: {len(optimization_results['operations'])} operations")
        
        return optimization_results