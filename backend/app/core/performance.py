"""Performance monitoring decorators and utilities."""

import asyncio
import functools
import logging
import time
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from contextlib import asynccontextmanager

from app.services.database_optimization import db_optimization_service
from app.core.cache import cache_manager

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


def monitor_query_performance(query_name: str):
    """Decorator to monitor database query performance."""
    def decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                async with db_optimization_service.query_performance_monitor(query_name):
                    return await func(*args, **kwargs)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # Log slow queries
                    if execution_time > db_optimization_service.slow_query_threshold:
                        logger.warning(f"Slow query detected: {query_name} took {execution_time:.2f}s")
                    
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    logger.error(f"Query {query_name} failed after {execution_time:.2f}s: {e}")
                    raise
            return sync_wrapper
    return decorator


def cache_result(
    cache_key_template: str,
    ttl: Optional[int] = None,
    jurisdiction_aware: bool = False
):
    """Decorator to cache function results with optional jurisdiction awareness."""
    def decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = cache_key_template.format(*args, **kwargs)
                
                # Add jurisdiction to cache key if requested
                if jurisdiction_aware and 'jurisdiction' in kwargs:
                    cache_key = f"{cache_key}:jurisdiction:{kwargs['jurisdiction']}"
                
                # Try to get from cache first
                cached_result = await cache_manager.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return cached_result
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                
                if result is not None:
                    await cache_manager.set(cache_key, result, ttl)
                    logger.debug(f"Cached result for key: {cache_key}")
                
                return result
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                # For sync functions, we can't use async cache operations
                # This would need to be implemented differently or converted to async
                logger.warning(f"Cache decorator used on sync function {func.__name__}, caching skipped")
                return func(*args, **kwargs)
            return sync_wrapper
    return decorator


def measure_execution_time(log_slow_threshold: float = 1.0):
    """Decorator to measure and log function execution time."""
    def decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    if execution_time > log_slow_threshold:
                        logger.warning(f"Slow execution: {func.__name__} took {execution_time:.2f}s")
                    else:
                        logger.debug(f"Execution time: {func.__name__} took {execution_time:.3f}s")
                    
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    logger.error(f"Function {func.__name__} failed after {execution_time:.2f}s: {e}")
                    raise
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    if execution_time > log_slow_threshold:
                        logger.warning(f"Slow execution: {func.__name__} took {execution_time:.2f}s")
                    else:
                        logger.debug(f"Execution time: {func.__name__} took {execution_time:.3f}s")
                    
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    logger.error(f"Function {func.__name__} failed after {execution_time:.2f}s: {e}")
                    raise
            return sync_wrapper
    return decorator


@asynccontextmanager
async def performance_context(operation_name: str, log_threshold: float = 1.0):
    """Context manager for measuring performance of code blocks."""
    start_time = time.time()
    try:
        yield
    finally:
        execution_time = time.time() - start_time
        
        if execution_time > log_threshold:
            logger.warning(f"Slow operation: {operation_name} took {execution_time:.2f}s")
        else:
            logger.debug(f"Operation time: {operation_name} took {execution_time:.3f}s")


class PerformanceMetrics:
    """Class for collecting and managing performance metrics."""
    
    def __init__(self):
        """Initialize performance metrics collector."""
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self.operation_counts: Dict[str, int] = {}
    
    def record_operation(
        self,
        operation_name: str,
        execution_time: float,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record performance metrics for an operation."""
        if operation_name not in self.metrics:
            self.metrics[operation_name] = {
                "total_time": 0.0,
                "total_calls": 0,
                "success_calls": 0,
                "failed_calls": 0,
                "avg_time": 0.0,
                "min_time": float('inf'),
                "max_time": 0.0,
                "metadata": []
            }
        
        metrics = self.metrics[operation_name]
        metrics["total_time"] += execution_time
        metrics["total_calls"] += 1
        
        if success:
            metrics["success_calls"] += 1
        else:
            metrics["failed_calls"] += 1
        
        metrics["avg_time"] = metrics["total_time"] / metrics["total_calls"]
        metrics["min_time"] = min(metrics["min_time"], execution_time)
        metrics["max_time"] = max(metrics["max_time"], execution_time)
        
        if metadata:
            metrics["metadata"].append({
                "timestamp": time.time(),
                "execution_time": execution_time,
                "success": success,
                **metadata
            })
            
            # Keep only last 100 metadata entries
            if len(metrics["metadata"]) > 100:
                metrics["metadata"] = metrics["metadata"][-100:]
    
    def get_metrics(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """Get performance metrics for an operation or all operations."""
        if operation_name:
            return self.metrics.get(operation_name, {})
        return self.metrics
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all performance metrics."""
        total_operations = sum(m["total_calls"] for m in self.metrics.values())
        total_time = sum(m["total_time"] for m in self.metrics.values())
        
        slowest_operations = sorted(
            [(name, m["max_time"]) for name, m in self.metrics.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        most_frequent_operations = sorted(
            [(name, m["total_calls"]) for name, m in self.metrics.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "total_operations": total_operations,
            "total_time": total_time,
            "avg_time_per_operation": total_time / total_operations if total_operations > 0 else 0,
            "slowest_operations": slowest_operations,
            "most_frequent_operations": most_frequent_operations,
            "operation_count": len(self.metrics)
        }
    
    def reset_metrics(self, operation_name: Optional[str] = None):
        """Reset metrics for an operation or all operations."""
        if operation_name:
            if operation_name in self.metrics:
                del self.metrics[operation_name]
        else:
            self.metrics.clear()
            self.operation_counts.clear()


# Global performance metrics instance
performance_metrics = PerformanceMetrics()


def track_performance(operation_name: str, include_metadata: bool = False):
    """Decorator to track performance metrics for functions."""
    def decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                metadata = {}
                
                try:
                    result = await func(*args, **kwargs)
                    
                    if include_metadata:
                        metadata = {
                            "args_count": len(args),
                            "kwargs_count": len(kwargs),
                            "result_type": type(result).__name__
                        }
                    
                    return result
                except Exception as e:
                    success = False
                    if include_metadata:
                        metadata = {
                            "error_type": type(e).__name__,
                            "error_message": str(e)
                        }
                    raise
                finally:
                    execution_time = time.time() - start_time
                    performance_metrics.record_operation(
                        operation_name, execution_time, success, metadata if include_metadata else None
                    )
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                metadata = {}
                
                try:
                    result = func(*args, **kwargs)
                    
                    if include_metadata:
                        metadata = {
                            "args_count": len(args),
                            "kwargs_count": len(kwargs),
                            "result_type": type(result).__name__
                        }
                    
                    return result
                except Exception as e:
                    success = False
                    if include_metadata:
                        metadata = {
                            "error_type": type(e).__name__,
                            "error_message": str(e)
                        }
                    raise
                finally:
                    execution_time = time.time() - start_time
                    performance_metrics.record_operation(
                        operation_name, execution_time, success, metadata if include_metadata else None
                    )
            return sync_wrapper
    return decorator


# Utility functions for common performance patterns

async def cached_database_query(
    cache_key: str,
    query_func: Callable,
    ttl: Optional[int] = None,
    *args,
    **kwargs
) -> Any:
    """Execute a database query with caching."""
    # Try cache first
    cached_result = await cache_manager.get(cache_key)
    if cached_result is not None:
        logger.debug(f"Database query cache hit: {cache_key}")
        return cached_result
    
    # Execute query with performance monitoring
    async with performance_context(f"db_query:{cache_key}"):
        result = await query_func(*args, **kwargs)
    
    # Cache the result
    if result is not None:
        await cache_manager.set(cache_key, result, ttl)
        logger.debug(f"Cached database query result: {cache_key}")
    
    return result


async def jurisdiction_aware_cached_query(
    base_cache_key: str,
    jurisdiction: str,
    query_func: Callable,
    ttl: Optional[int] = None,
    *args,
    **kwargs
) -> Any:
    """Execute a jurisdiction-aware database query with caching."""
    cache_key = f"{base_cache_key}:jurisdiction:{jurisdiction}"
    return await cached_database_query(cache_key, query_func, ttl, *args, **kwargs)