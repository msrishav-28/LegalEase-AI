"""Task monitoring and management utilities."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from celery.result import AsyncResult
from celery import states

from app.celery_app.celery import celery_app, TaskProgress

logger = logging.getLogger(__name__)


class TaskMonitor:
    """Utility class for monitoring and managing Celery tasks."""
    
    def __init__(self):
        self.celery_app = celery_app
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a specific task.
        
        Args:
            task_id: The ID of the task to check
            
        Returns:
            Dict containing task status information
        """
        try:
            result = AsyncResult(task_id, app=self.celery_app)
            
            status_info = {
                "task_id": task_id,
                "state": result.state,
                "ready": result.ready(),
                "successful": result.successful(),
                "failed": result.failed(),
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            if result.state == states.PENDING:
                status_info["info"] = "Task is waiting to be processed"
            elif result.state == states.PROGRESS:
                status_info["info"] = result.result
                status_info["progress"] = TaskProgress.get_progress(task_id)
            elif result.state == states.SUCCESS:
                status_info["result"] = result.result
                status_info["info"] = "Task completed successfully"
            elif result.state == states.FAILURE:
                status_info["error"] = str(result.result)
                status_info["traceback"] = result.traceback
                status_info["info"] = "Task failed"
            else:
                status_info["info"] = f"Task state: {result.state}"
            
            return status_info
            
        except Exception as exc:
            logger.error(f"Failed to get task status for {task_id}: {exc}")
            return {
                "task_id": task_id,
                "state": "ERROR",
                "error": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
            }
    
    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """
        Get list of currently active tasks.
        
        Returns:
            List of active task information
        """
        try:
            inspect = self.celery_app.control.inspect()
            active_tasks = inspect.active()
            
            if not active_tasks:
                return []
            
            tasks = []
            for worker, task_list in active_tasks.items():
                for task in task_list:
                    tasks.append({
                        "task_id": task["id"],
                        "name": task["name"],
                        "worker": worker,
                        "args": task.get("args", []),
                        "kwargs": task.get("kwargs", {}),
                        "time_start": task.get("time_start"),
                    })
            
            return tasks
            
        except Exception as exc:
            logger.error(f"Failed to get active tasks: {exc}")
            return []
    
    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """
        Get list of scheduled tasks.
        
        Returns:
            List of scheduled task information
        """
        try:
            inspect = self.celery_app.control.inspect()
            scheduled_tasks = inspect.scheduled()
            
            if not scheduled_tasks:
                return []
            
            tasks = []
            for worker, task_list in scheduled_tasks.items():
                for task in task_list:
                    tasks.append({
                        "task_id": task["request"]["id"],
                        "name": task["request"]["task"],
                        "worker": worker,
                        "eta": task.get("eta"),
                        "priority": task["request"].get("priority"),
                    })
            
            return tasks
            
        except Exception as exc:
            logger.error(f"Failed to get scheduled tasks: {exc}")
            return []
    
    def get_worker_stats(self) -> Dict[str, Any]:
        """
        Get worker statistics.
        
        Returns:
            Dict containing worker statistics
        """
        try:
            inspect = self.celery_app.control.inspect()
            stats = inspect.stats()
            
            if not stats:
                return {"workers": 0, "details": {}}
            
            worker_info = {}
            for worker, worker_stats in stats.items():
                worker_info[worker] = {
                    "status": "online",
                    "pool": worker_stats.get("pool", {}),
                    "total_tasks": worker_stats.get("total", {}),
                    "rusage": worker_stats.get("rusage", {}),
                }
            
            return {
                "workers": len(worker_info),
                "details": worker_info,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as exc:
            logger.error(f"Failed to get worker stats: {exc}")
            return {
                "workers": 0,
                "error": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
            }
    
    def cancel_task(self, task_id: str, terminate: bool = False) -> Dict[str, Any]:
        """
        Cancel a running task.
        
        Args:
            task_id: The ID of the task to cancel
            terminate: Whether to terminate the task forcefully
            
        Returns:
            Dict containing cancellation result
        """
        try:
            if terminate:
                self.celery_app.control.terminate(task_id)
                action = "terminated"
            else:
                self.celery_app.control.revoke(task_id, terminate=False)
                action = "revoked"
            
            return {
                "task_id": task_id,
                "action": action,
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as exc:
            logger.error(f"Failed to cancel task {task_id}: {exc}")
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
            }
    
    def purge_queue(self, queue_name: str = None) -> Dict[str, Any]:
        """
        Purge tasks from a queue.
        
        Args:
            queue_name: Name of the queue to purge (None for all queues)
            
        Returns:
            Dict containing purge result
        """
        try:
            if queue_name:
                purged = self.celery_app.control.purge()
            else:
                # Purge specific queue
                with self.celery_app.connection() as conn:
                    conn.default_channel.queue_purge(queue_name)
                purged = {"purged": "unknown"}  # Queue-specific purge doesn't return count
            
            return {
                "queue": queue_name or "all",
                "status": "success",
                "purged_tasks": purged,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as exc:
            logger.error(f"Failed to purge queue {queue_name}: {exc}")
            return {
                "queue": queue_name or "all",
                "status": "failed",
                "error": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
            }
    
    def get_queue_length(self, queue_name: str) -> int:
        """
        Get the number of tasks in a queue.
        
        Args:
            queue_name: Name of the queue to check
            
        Returns:
            Number of tasks in the queue
        """
        try:
            with self.celery_app.connection() as conn:
                return conn.default_channel.client.llen(f"celery.{queue_name}")
        except Exception as exc:
            logger.error(f"Failed to get queue length for {queue_name}: {exc}")
            return -1
    
    def get_task_history(
        self, 
        limit: int = 100, 
        task_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get task execution history.
        
        Args:
            limit: Maximum number of tasks to return
            task_name: Filter by specific task name
            
        Returns:
            List of task history information
        """
        try:
            # This would typically require a custom result backend
            # or integration with monitoring tools like Flower
            # For now, return empty list as placeholder
            return []
            
        except Exception as exc:
            logger.error(f"Failed to get task history: {exc}")
            return []


class TaskRetryManager:
    """Utility class for managing task retries."""
    
    def __init__(self):
        self.celery_app = celery_app
    
    def retry_failed_tasks(
        self, 
        task_name: Optional[str] = None,
        max_age_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Retry failed tasks within a time window.
        
        Args:
            task_name: Specific task name to retry (None for all)
            max_age_hours: Maximum age of failed tasks to retry
            
        Returns:
            Dict containing retry results
        """
        try:
            # This would require storing failed task information
            # and implementing retry logic based on the storage
            # For now, return placeholder result
            
            return {
                "status": "success",
                "retried_tasks": 0,
                "task_name": task_name,
                "max_age_hours": max_age_hours,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as exc:
            logger.error(f"Failed to retry failed tasks: {exc}")
            return {
                "status": "failed",
                "error": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
            }


# Global instances
task_monitor = TaskMonitor()
retry_manager = TaskRetryManager()