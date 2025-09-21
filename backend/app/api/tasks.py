"""Task management and monitoring API endpoints."""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from pydantic import BaseModel, Field

from app.core.dependencies import get_current_user
from app.celery_app.monitoring import task_monitor, retry_manager
from app.celery_app.celery import celery_app, TaskProgress
from app.celery_app.tasks.ai_analysis import (
    comprehensive_document_analysis_task,
    jurisdiction_specific_analysis_task,
    batch_document_analysis_task
)
from app.core.cache import cache_manager
from app.schemas.base import BaseResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Task Management"])


# Request/Response Models
class StartAnalysisRequest(BaseModel):
    """Request model for starting document analysis."""
    document_id: str = Field(..., description="Document ID to analyze")
    analysis_type: str = Field("comprehensive", description="Type of analysis to perform")
    analysis_options: Optional[Dict[str, Any]] = Field(None, description="Additional analysis options")


class StartJurisdictionAnalysisRequest(BaseModel):
    """Request model for starting jurisdiction-specific analysis."""
    document_id: str = Field(..., description="Document ID to analyze")
    jurisdiction: str = Field(..., description="Legal jurisdiction")
    analysis_type: str = Field(..., description="Specific analysis type")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional parameters")


class StartBatchAnalysisRequest(BaseModel):
    """Request model for starting batch analysis."""
    document_ids: List[str] = Field(..., description="List of document IDs to analyze")
    analysis_type: str = Field("comprehensive", description="Type of analysis to perform")
    batch_options: Optional[Dict[str, Any]] = Field(None, description="Batch processing options")


class TaskResponse(BaseResponse):
    """Response model for task operations."""
    task_id: str
    status: str
    message: Optional[str] = None
    progress: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None


class TaskListResponse(BaseResponse):
    """Response model for task list operations."""
    tasks: List[Dict[str, Any]]
    total_count: int


# Task Management Endpoints

@router.post("/analysis/start", response_model=TaskResponse)
async def start_document_analysis(
    request: StartAnalysisRequest,
    current_user = Depends(get_current_user)
) -> TaskResponse:
    """
    Start comprehensive document analysis task.
    
    This endpoint starts a background task for comprehensive document analysis
    including jurisdiction detection, AI analysis, and jurisdiction-specific processing.
    """
    try:
        logger.info(f"Starting document analysis for document {request.document_id} by user {current_user.id}")
        
        # Start the Celery task
        task = comprehensive_document_analysis_task.delay(
            document_id=request.document_id,
            user_id=str(current_user.id),
            analysis_options=request.analysis_options
        )
        
        return TaskResponse(
            success=True,
            message="Document analysis task started successfully",
            task_id=task.id,
            status="started"
        )
        
    except Exception as e:
        logger.error(f"Failed to start document analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start analysis task: {str(e)}"
        )


@router.post("/analysis/jurisdiction", response_model=TaskResponse)
async def start_jurisdiction_analysis(
    request: StartJurisdictionAnalysisRequest,
    current_user = Depends(get_current_user)
) -> TaskResponse:
    """
    Start jurisdiction-specific analysis task.
    
    This endpoint starts a background task for jurisdiction-specific analysis
    such as stamp duty calculation, UCC analysis, or cross-border comparison.
    """
    try:
        logger.info(f"Starting {request.jurisdiction} {request.analysis_type} analysis for document {request.document_id}")
        
        # Start the Celery task
        task = jurisdiction_specific_analysis_task.delay(
            document_id=request.document_id,
            jurisdiction=request.jurisdiction,
            analysis_type=request.analysis_type,
            user_id=str(current_user.id),
            parameters=request.parameters
        )
        
        return TaskResponse(
            success=True,
            message=f"Jurisdiction-specific {request.analysis_type} task started successfully",
            task_id=task.id,
            status="started"
        )
        
    except Exception as e:
        logger.error(f"Failed to start jurisdiction analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start jurisdiction analysis task: {str(e)}"
        )


@router.post("/analysis/batch", response_model=TaskResponse)
async def start_batch_analysis(
    request: StartBatchAnalysisRequest,
    current_user = Depends(get_current_user)
) -> TaskResponse:
    """
    Start batch document analysis task.
    
    This endpoint starts a background task for analyzing multiple documents
    in batch with the specified analysis type.
    """
    try:
        logger.info(f"Starting batch {request.analysis_type} analysis for {len(request.document_ids)} documents")
        
        # Start the Celery task
        task = batch_document_analysis_task.delay(
            document_ids=request.document_ids,
            analysis_type=request.analysis_type,
            user_id=str(current_user.id),
            batch_options=request.batch_options
        )
        
        return TaskResponse(
            success=True,
            message=f"Batch analysis task started successfully for {len(request.document_ids)} documents",
            task_id=task.id,
            status="started"
        )
        
    except Exception as e:
        logger.error(f"Failed to start batch analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start batch analysis task: {str(e)}"
        )


# Task Status and Monitoring Endpoints

@router.get("/status/{task_id}", response_model=TaskResponse)
async def get_task_status(
    task_id: str,
    current_user = Depends(get_current_user)
) -> TaskResponse:
    """
    Get the status of a specific task.
    
    Returns detailed information about task progress, current state,
    and results if completed.
    """
    try:
        # Try to get cached progress first
        cached_progress = await TaskProgress.get_cached_progress(task_id)
        
        # Get detailed task status
        task_status = task_monitor.get_task_status(task_id)
        
        # Check if task result is cached
        cached_result = await cache_manager.get_task_result(task_id)
        
        return TaskResponse(
            success=True,
            message="Task status retrieved successfully",
            task_id=task_id,
            status=task_status.get("state", "unknown"),
            progress=cached_progress or task_status.get("info"),
            result=cached_result.get("result") if cached_result else task_status.get("result")
        )
        
    except Exception as e:
        logger.error(f"Failed to get task status for {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found or error retrieving status: {str(e)}"
        )


@router.get("/progress/{task_id}")
async def get_task_progress(
    task_id: str,
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get real-time progress information for a task.
    
    Returns progress percentage, current step, and estimated completion time.
    """
    try:
        # Get cached progress for better performance
        progress = await TaskProgress.get_cached_progress(task_id)
        
        return {
            "task_id": task_id,
            "progress": progress,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Failed to get task progress for {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task progress not found: {str(e)}"
        )


@router.get("/active", response_model=TaskListResponse)
async def get_active_tasks(
    current_user = Depends(get_current_user)
) -> TaskListResponse:
    """
    Get list of currently active tasks.
    
    Returns information about all tasks currently being processed
    by Celery workers.
    """
    try:
        active_tasks = task_monitor.get_active_tasks()
        
        return TaskListResponse(
            success=True,
            message="Active tasks retrieved successfully",
            tasks=active_tasks,
            total_count=len(active_tasks)
        )
        
    except Exception as e:
        logger.error(f"Failed to get active tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve active tasks: {str(e)}"
        )


@router.get("/scheduled", response_model=TaskListResponse)
async def get_scheduled_tasks(
    current_user = Depends(get_current_user)
) -> TaskListResponse:
    """
    Get list of scheduled tasks.
    
    Returns information about tasks that are scheduled to run
    at a future time.
    """
    try:
        scheduled_tasks = task_monitor.get_scheduled_tasks()
        
        return TaskListResponse(
            success=True,
            message="Scheduled tasks retrieved successfully",
            tasks=scheduled_tasks,
            total_count=len(scheduled_tasks)
        )
        
    except Exception as e:
        logger.error(f"Failed to get scheduled tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve scheduled tasks: {str(e)}"
        )


@router.get("/workers")
async def get_worker_stats(
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get Celery worker statistics.
    
    Returns information about active workers, their status,
    and performance metrics.
    """
    try:
        worker_stats = task_monitor.get_worker_stats()
        
        return {
            "success": True,
            "message": "Worker statistics retrieved successfully",
            "worker_stats": worker_stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get worker stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve worker statistics: {str(e)}"
        )


# Task Control Endpoints

@router.post("/cancel/{task_id}")
async def cancel_task(
    task_id: str,
    terminate: bool = False,
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Cancel a running task.
    
    Args:
        task_id: ID of the task to cancel
        terminate: Whether to forcefully terminate the task
    """
    try:
        result = task_monitor.cancel_task(task_id, terminate)
        
        return {
            "success": True,
            "message": f"Task {'terminated' if terminate else 'cancelled'} successfully",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Failed to cancel task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel task: {str(e)}"
        )


@router.post("/retry/{task_id}")
async def retry_task(
    task_id: str,
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retry a failed task.
    
    This endpoint attempts to restart a failed task with the same parameters.
    """
    try:
        # Get the original task result to extract parameters
        task_status = task_monitor.get_task_status(task_id)
        
        if task_status.get("state") != "FAILURE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task is not in failed state"
            )
        
        # For now, return a placeholder response
        # In a full implementation, you'd need to store task parameters
        # and recreate the task with the same parameters
        
        return {
            "success": True,
            "message": "Task retry functionality is not yet implemented",
            "task_id": task_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retry task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retry task: {str(e)}"
        )


# Cache Management Endpoints

@router.get("/cache/stats")
async def get_cache_stats(
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get cache statistics and performance metrics.
    
    Returns information about Redis cache usage, hit rates,
    and memory consumption.
    """
    try:
        if not cache_manager.redis_client:
            await cache_manager.connect()
        
        cache_stats = await cache_manager.get_cache_stats()
        
        return {
            "success": True,
            "message": "Cache statistics retrieved successfully",
            "cache_stats": cache_stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve cache statistics: {str(e)}"
        )


@router.post("/cache/clear/{task_id}")
async def clear_task_cache(
    task_id: str,
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Clear cached data for a specific task.
    
    Removes task progress, results, and related cached data.
    """
    try:
        if not cache_manager.redis_client:
            await cache_manager.connect()
        
        deleted_count = await cache_manager.delete_task_cache(task_id)
        
        return {
            "success": True,
            "message": f"Cleared {deleted_count} cache entries for task {task_id}",
            "task_id": task_id,
            "deleted_entries": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Failed to clear task cache for {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear task cache: {str(e)}"
        )


@router.post("/cache/clear/document/{document_id}")
async def clear_document_analysis_cache(
    document_id: str,
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Clear cached analysis results for a specific document.
    
    Removes all cached analysis results for the specified document,
    forcing fresh analysis on next request.
    """
    try:
        if not cache_manager.redis_client:
            await cache_manager.connect()
        
        deleted_count = await cache_manager.invalidate_document_analysis_cache(document_id)
        
        return {
            "success": True,
            "message": f"Cleared {deleted_count} analysis cache entries for document {document_id}",
            "document_id": document_id,
            "deleted_entries": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Failed to clear document analysis cache for {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear document analysis cache: {str(e)}"
        )


# Queue Management Endpoints

@router.get("/queues")
async def get_queue_info(
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get information about task queues.
    
    Returns queue lengths, processing rates, and queue health status.
    """
    try:
        queue_info = {}
        queue_names = ["document_processing", "ai_analysis", "jurisdiction_analysis", "celery"]
        
        for queue_name in queue_names:
            queue_length = task_monitor.get_queue_length(queue_name)
            queue_info[queue_name] = {
                "length": queue_length,
                "status": "healthy" if queue_length >= 0 else "error"
            }
        
        return {
            "success": True,
            "message": "Queue information retrieved successfully",
            "queues": queue_info
        }
        
    except Exception as e:
        logger.error(f"Failed to get queue info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve queue information: {str(e)}"
        )


@router.post("/queues/purge/{queue_name}")
async def purge_queue(
    queue_name: str,
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Purge all tasks from a specific queue.
    
    WARNING: This will remove all pending tasks from the specified queue.
    Use with caution in production environments.
    """
    try:
        result = task_monitor.purge_queue(queue_name)
        
        return {
            "success": True,
            "message": f"Queue {queue_name} purged successfully",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Failed to purge queue {queue_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to purge queue: {str(e)}"
        )