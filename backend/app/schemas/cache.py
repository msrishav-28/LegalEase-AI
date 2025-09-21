"""Pydantic schemas for cache management API."""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


class CacheStatsResponse(BaseModel):
    """Response model for cache statistics."""
    status: str
    stats: Dict[str, Any]


class JurisdictionCacheStatsResponse(BaseModel):
    """Response model for jurisdiction-specific cache statistics."""
    status: str
    jurisdiction: str
    stats: Dict[str, Any]


class CacheWarmingRequest(BaseModel):
    """Request model for cache warming."""
    background: bool = Field(default=True, description="Whether to run warming in background")
    jurisdictions: Optional[List[str]] = Field(default=None, description="Specific jurisdictions to warm")
    categories: Optional[List[str]] = Field(default=None, description="Specific cache categories to warm")


class CacheWarmingResponse(BaseModel):
    """Response model for cache warming."""
    status: str
    message: str
    background: bool
    results: Optional[Dict[str, Any]] = None
    duration_seconds: Optional[float] = None


class CacheInvalidationRequest(BaseModel):
    """Request model for cache invalidation."""
    document_id: Optional[str] = Field(default=None, description="Document ID to invalidate cache for")
    jurisdiction: Optional[str] = Field(default=None, description="Jurisdiction to invalidate cache for")
    cache_pattern: Optional[str] = Field(default=None, description="Cache key pattern to invalidate")


class CacheInvalidationResponse(BaseModel):
    """Response model for cache invalidation."""
    status: str
    deleted_count: int
    message: str


class CacheKeyInfo(BaseModel):
    """Information about a cache key."""
    key: str
    ttl: Optional[int] = None
    size_bytes: Optional[int] = None
    created_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None


class CacheAnalysisRequest(BaseModel):
    """Request model for caching analysis results."""
    document_id: str
    analysis_type: str
    jurisdiction: Optional[str] = None
    result: Dict[str, Any]
    ttl: Optional[int] = Field(default=None, description="Time to live in seconds")


class CacheAnalysisResponse(BaseModel):
    """Response model for cached analysis results."""
    status: str
    cached: bool
    cache_key: str
    ttl: Optional[int] = None


class BatchCacheRequest(BaseModel):
    """Request model for batch caching operations."""
    analyses: List[Dict[str, Any]]
    ttl: Optional[int] = Field(default=None, description="Time to live in seconds")


class BatchCacheResponse(BaseModel):
    """Response model for batch caching operations."""
    status: str
    cached_count: int
    failed_count: int
    total_count: int


class CacheSearchRequest(BaseModel):
    """Request model for searching cache entries."""
    pattern: str = Field(description="Search pattern for cache keys")
    limit: int = Field(default=100, description="Maximum number of results")
    include_values: bool = Field(default=False, description="Whether to include cached values")


class CacheSearchResponse(BaseModel):
    """Response model for cache search results."""
    status: str
    total_found: int
    results: List[CacheKeyInfo]
    has_more: bool


class CacheMetrics(BaseModel):
    """Cache performance metrics."""
    hit_rate: float = Field(description="Cache hit rate percentage")
    miss_rate: float = Field(description="Cache miss rate percentage")
    total_requests: int = Field(description="Total cache requests")
    total_hits: int = Field(description="Total cache hits")
    total_misses: int = Field(description="Total cache misses")
    memory_usage: str = Field(description="Memory usage in human readable format")
    key_count: int = Field(description="Total number of keys in cache")
    expired_keys: int = Field(description="Number of expired keys")


class CacheMetricsResponse(BaseModel):
    """Response model for cache metrics."""
    status: str
    metrics: CacheMetrics
    timestamp: datetime


class CacheConfigRequest(BaseModel):
    """Request model for cache configuration updates."""
    default_ttl: Optional[int] = Field(default=None, description="Default TTL in seconds")
    analysis_ttl: Optional[int] = Field(default=None, description="Analysis results TTL in seconds")
    task_ttl: Optional[int] = Field(default=None, description="Task data TTL in seconds")
    max_memory: Optional[str] = Field(default=None, description="Maximum memory usage")


class CacheConfigResponse(BaseModel):
    """Response model for cache configuration."""
    status: str
    config: Dict[str, Any]
    message: str


class JurisdictionWarmingRequest(BaseModel):
    """Request model for jurisdiction-specific cache warming."""
    document_types: List[str] = Field(default=["contract", "agreement", "mou", "nda"])
    analysis_types: List[str] = Field(default=["comprehensive", "risk_analysis", "compliance_check"])
    force_refresh: bool = Field(default=False, description="Force refresh existing cache entries")


class DocumentCacheWarmingRequest(BaseModel):
    """Request model for document-specific cache warming."""
    document_type: str
    jurisdiction: str
    preload_templates: bool = Field(default=True, description="Preload document templates")
    preload_compliance: bool = Field(default=True, description="Preload compliance requirements")


class CacheHealthResponse(BaseModel):
    """Response model for cache health check."""
    status: str
    message: Optional[str] = None
    error: Optional[str] = None
    checks: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CacheOperationLog(BaseModel):
    """Log entry for cache operations."""
    operation: str = Field(description="Type of cache operation")
    key: str = Field(description="Cache key involved")
    success: bool = Field(description="Whether operation was successful")
    duration_ms: float = Field(description="Operation duration in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = Field(default=None, description="Error message if operation failed")


class CacheOperationLogResponse(BaseModel):
    """Response model for cache operation logs."""
    status: str
    logs: List[CacheOperationLog]
    total_count: int
    page: int
    page_size: int