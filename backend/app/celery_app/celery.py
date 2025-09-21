"""Celery application configuration and setup."""

from celery import Celery
from celery.signals import worker_ready, worker_shutdown
from kombu import Queue
import logging
import os

from app.config import get_settings

settings = get_settings()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Celery instance
celery_app = Celery(
    "legalease_ai",
    broker=settings.rabbitmq_url,
    backend=settings.redis_url,
    include=[
        "app.celery_app.tasks.document_processing",
        "app.celery_app.tasks.ai_analysis",
        "app.celery_app.tasks.jurisdiction_analysis",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        "app.celery_app.tasks.document_processing.*": {"queue": "document_processing"},
        "app.celery_app.tasks.ai_analysis.*": {"queue": "ai_analysis"},
        "app.celery_app.tasks.jurisdiction_analysis.*": {"queue": "jurisdiction_analysis"},
    },
    
    # Queue definitions
    task_queues=(
        Queue("document_processing", routing_key="document_processing"),
        Queue("ai_analysis", routing_key="ai_analysis"),
        Queue("jurisdiction_analysis", routing_key="jurisdiction_analysis"),
        Queue("celery", routing_key="celery"),  # Default queue
    ),
    
    # Task execution settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task result settings
    result_expires=3600,  # 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",
        "visibility_timeout": 3600,
    },
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Retry settings
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    
    # Task time limits
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,  # 10 minutes
    
    # Beat schedule (for periodic tasks)
    beat_schedule={
        "cleanup-expired-results": {
            "task": "app.celery_app.tasks.maintenance.cleanup_expired_results",
            "schedule": 3600.0,  # Every hour
        },
        "health-check": {
            "task": "app.celery_app.tasks.maintenance.health_check",
            "schedule": 300.0,  # Every 5 minutes
        },
    },
)


@worker_ready.connect
def worker_ready_handler(sender=None, **kwargs):
    """Handle worker ready signal."""
    logger.info(f"Celery worker {sender} is ready")


@worker_shutdown.connect
def worker_shutdown_handler(sender=None, **kwargs):
    """Handle worker shutdown signal."""
    logger.info(f"Celery worker {sender} is shutting down")


# Task progress tracking
class TaskProgress:
    """Utility class for tracking task progress with WebSocket notifications and caching."""
    
    @staticmethod
    def update_progress(task_id: str, current: int, total: int, message: str = ""):
        """Update task progress with WebSocket notifications and caching."""
        from datetime import datetime
        import asyncio
        
        progress = {
            "current": current,
            "total": total,
            "percentage": int((current / total) * 100) if total > 0 else 0,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Update task state
        celery_app.backend.store_result(
            task_id,
            progress,
            "PROGRESS"
        )
        
        # Cache progress data and send notifications asynchronously
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            # If loop is already running, create tasks
            asyncio.create_task(TaskProgress._cache_progress(task_id, progress))
            asyncio.create_task(TaskProgress._notify_progress(task_id, progress))
        else:
            # If no loop is running, run the coroutines
            loop.run_until_complete(TaskProgress._cache_progress(task_id, progress))
            loop.run_until_complete(TaskProgress._notify_progress(task_id, progress))
        
        logger.info(f"Task {task_id}: {progress['percentage']}% - {message}")
    
    @staticmethod
    async def _cache_progress(task_id: str, progress_data: dict):
        """Cache progress data in Redis."""
        try:
            from app.core.cache import cache_manager
            
            if not cache_manager.redis_client:
                await cache_manager.connect()
            
            await cache_manager.cache_task_progress(
                task_id=task_id,
                progress=progress_data['current'],
                total=progress_data['total'],
                message=progress_data['message'],
                metadata=progress_data
            )
            
        except Exception as e:
            logger.error(f"Failed to cache progress for task {task_id}: {e}")
    
    @staticmethod
    async def _notify_progress(task_id: str, progress_data: dict):
        """Send WebSocket notification for progress update."""
        try:
            from app.api.websocket import notify_task_progress
            
            await notify_task_progress(
                task_id=task_id,
                progress=progress_data['current'],
                total=progress_data['total'],
                message=progress_data['message']
            )
            
        except Exception as e:
            logger.error(f"Failed to send progress notification for task {task_id}: {e}")
    
    @staticmethod
    def get_progress(task_id: str) -> dict:
        """Get task progress."""
        result = celery_app.AsyncResult(task_id)
        
        if result.state == "PROGRESS":
            return result.result
        elif result.state == "SUCCESS":
            return {
                "current": 100,
                "total": 100,
                "percentage": 100,
                "message": "Task completed successfully",
            }
        elif result.state == "FAILURE":
            return {
                "current": 0,
                "total": 100,
                "percentage": 0,
                "message": f"Task failed: {str(result.result)}",
            }
        else:
            return {
                "current": 0,
                "total": 100,
                "percentage": 0,
                "message": f"Task state: {result.state}",
            }
    
    @staticmethod
    async def get_cached_progress(task_id: str) -> dict:
        """Get cached progress data from Redis."""
        try:
            from app.core.cache import cache_manager
            
            if not cache_manager.redis_client:
                await cache_manager.connect()
            
            cached_progress = await cache_manager.get_task_progress(task_id)
            return cached_progress or TaskProgress.get_progress(task_id)
            
        except Exception as e:
            logger.error(f"Failed to get cached progress for task {task_id}: {e}")
            return TaskProgress.get_progress(task_id)
    
    @staticmethod
    async def notify_completion(task_id: str, result: dict):
        """Notify task completion via WebSocket and cache result."""
        try:
            # Cache the result
            from app.core.cache import cache_manager
            
            if not cache_manager.redis_client:
                await cache_manager.connect()
            
            await cache_manager.cache_task_result(task_id, result, "completed")
            
            # Send WebSocket notification
            from app.api.websocket import notify_task_completed
            await notify_task_completed(task_id, result)
            
        except Exception as e:
            logger.error(f"Failed to notify completion for task {task_id}: {e}")
    
    @staticmethod
    async def notify_failure(task_id: str, error: str):
        """Notify task failure via WebSocket and cache error."""
        try:
            # Cache the error
            from app.core.cache import cache_manager
            
            if not cache_manager.redis_client:
                await cache_manager.connect()
            
            await cache_manager.cache_task_result(
                task_id, 
                {"error": error}, 
                "failed"
            )
            
            # Send WebSocket notification
            from app.api.websocket import notify_task_failed
            await notify_task_failed(task_id, error)
            
        except Exception as e:
            logger.error(f"Failed to notify failure for task {task_id}: {e}")


# Error handling utilities
class TaskError(Exception):
    """Base exception for task errors."""
    pass


class DocumentProcessingError(TaskError):
    """Exception for document processing errors."""
    pass


class AIAnalysisError(TaskError):
    """Exception for AI analysis errors."""
    pass


class JurisdictionAnalysisError(TaskError):
    """Exception for jurisdiction analysis errors."""
    pass


def handle_task_error(task, exc, task_id, args, kwargs, einfo):
    """Global error handler for tasks."""
    logger.error(f"Task {task.name} failed: {exc}")
    logger.error(f"Task ID: {task_id}")
    logger.error(f"Args: {args}")
    logger.error(f"Kwargs: {kwargs}")
    logger.error(f"Exception info: {einfo}")
    
    # Update task progress with error
    TaskProgress.update_progress(
        task_id,
        0,
        100,
        f"Task failed: {str(exc)}"
    )


# Apply error handler to all tasks
celery_app.conf.task_annotations = {
    "*": {"on_failure": handle_task_error}
}