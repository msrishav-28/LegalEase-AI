"""Pydantic schemas for database optimization API."""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


class DatabaseStatsResponse(BaseModel):
    """Response model for database statistics."""
    status: str
    database_size: Optional[str] = None
    table_sizes: List[Dict[str, Any]] = []
    connection_pool: Dict[str, Any] = {}
    index_usage: List[Dict[str, Any]] = []


class IndexCreationResponse(BaseModel):
    """Response model for index creation."""
    status: str
    message: str
    indexes_created: Optional[List[str]] = None
    created_count: Optional[int] = None
    total_indexes: Optional[int] = None


class QueryPerformanceRequest(BaseModel):
    """Request model for query performance analysis."""
    query: str = Field(description="SQL query to analyze")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Query parameters")


class QueryPerformanceResponse(BaseModel):
    """Response model for query performance analysis."""
    status: str
    metrics: Dict[str, Any]
    execution_plan: Optional[Dict[str, Any]] = None


class SlowQueriesResponse(BaseModel):
    """Response model for slow queries."""
    status: str
    queries: List[Dict[str, Any]]
    total_count: int


class ConnectionPoolStatsResponse(BaseModel):
    """Response model for connection pool statistics."""
    status: str
    stats: Dict[str, Any]


class DatabaseOptimizationRequest(BaseModel):
    """Request model for database optimization operations."""
    update_statistics: bool = Field(default=True, description="Update table statistics")
    vacuum_analyze: bool = Field(default=False, description="Perform VACUUM ANALYZE")
    create_indexes: bool = Field(default=False, description="Create missing indexes")
    background: bool = Field(default=True, description="Run operations in background")


class DatabaseOptimizationResponse(BaseModel):
    """Response model for database optimization operations."""
    status: str
    operations: Dict[str, Any]
    background: bool


class IndexUsageStats(BaseModel):
    """Model for index usage statistics."""
    schema: str
    table: str
    index: str
    tuples_read: int
    tuples_fetched: int
    scans: int


class TableSizeInfo(BaseModel):
    """Model for table size information."""
    schema: str
    table: str
    size: str
    size_bytes: int


class QueryStatistics(BaseModel):
    """Model for query performance statistics."""
    total_calls: int
    total_time: float
    avg_time: float
    max_time: float
    min_time: float


class DatabaseHealthResponse(BaseModel):
    """Response model for database health check."""
    status: str
    issues: List[str] = []
    connection_pool: Dict[str, Any] = {}
    database_accessible: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MaintenanceRequest(BaseModel):
    """Request model for database maintenance operations."""
    operation: str = Field(description="Maintenance operation type")
    tables: Optional[List[str]] = Field(default=None, description="Specific tables to maintain")
    background: bool = Field(default=True, description="Run in background")


class MaintenanceResponse(BaseModel):
    """Response model for database maintenance operations."""
    status: str
    message: str
    operation: str
    affected_tables: Optional[List[str]] = None


class DatabaseMetrics(BaseModel):
    """Model for database performance metrics."""
    database_size: str
    total_connections: int
    active_connections: int
    connection_utilization: float
    cache_hit_ratio: float
    transactions_per_second: float
    queries_per_second: float
    slow_query_count: int


class DatabaseMetricsResponse(BaseModel):
    """Response model for database metrics."""
    status: str
    metrics: DatabaseMetrics
    timestamp: datetime


class IndexRecommendation(BaseModel):
    """Model for index recommendations."""
    table: str
    columns: List[str]
    index_type: str
    estimated_benefit: str
    reason: str
    sql: str


class IndexRecommendationsResponse(BaseModel):
    """Response model for index recommendations."""
    status: str
    recommendations: List[IndexRecommendation]
    total_recommendations: int


class QueryOptimizationSuggestion(BaseModel):
    """Model for query optimization suggestions."""
    query_pattern: str
    issue: str
    suggestion: str
    estimated_improvement: str
    example_fix: Optional[str] = None


class QueryOptimizationResponse(BaseModel):
    """Response model for query optimization suggestions."""
    status: str
    suggestions: List[QueryOptimizationSuggestion]
    total_suggestions: int


class DatabaseConfigRequest(BaseModel):
    """Request model for database configuration updates."""
    connection_pool_size: Optional[int] = Field(default=None, description="Connection pool size")
    max_overflow: Optional[int] = Field(default=None, description="Maximum overflow connections")
    slow_query_threshold: Optional[float] = Field(default=None, description="Slow query threshold in seconds")


class DatabaseConfigResponse(BaseModel):
    """Response model for database configuration."""
    status: str
    config: Dict[str, Any]
    message: str


class BackupRequest(BaseModel):
    """Request model for database backup operations."""
    backup_type: str = Field(description="Type of backup (full, incremental)")
    tables: Optional[List[str]] = Field(default=None, description="Specific tables to backup")
    compression: bool = Field(default=True, description="Enable compression")


class BackupResponse(BaseModel):
    """Response model for database backup operations."""
    status: str
    backup_id: str
    backup_path: str
    size: str
    duration_seconds: float


class RestoreRequest(BaseModel):
    """Request model for database restore operations."""
    backup_id: str = Field(description="Backup ID to restore from")
    tables: Optional[List[str]] = Field(default=None, description="Specific tables to restore")
    point_in_time: Optional[datetime] = Field(default=None, description="Point in time to restore to")


class RestoreResponse(BaseModel):
    """Response model for database restore operations."""
    status: str
    restored_tables: List[str]
    duration_seconds: float
    message: str