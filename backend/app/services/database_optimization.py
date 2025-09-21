"""Database optimization service for performance monitoring and query optimization."""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy.sql import Select
from sqlalchemy.orm import Query

from app.database.connection import engine, AsyncSessionLocal
from app.core.cache import cache_manager

logger = logging.getLogger(__name__)


class DatabaseOptimizationService:
    """Service for database performance optimization and monitoring."""
    
    def __init__(self):
        """Initialize database optimization service."""
        self.query_stats: Dict[str, Dict[str, Any]] = {}
        self.slow_query_threshold = 1.0  # seconds
        self.connection_pool_stats: Dict[str, Any] = {}
        
    async def create_jurisdiction_indexes(self) -> Dict[str, Any]:
        """Create jurisdiction-specific database indexes for optimal query performance."""
        try:
            async with AsyncSessionLocal() as session:
                indexes_created = []
                
                # Document indexes for jurisdiction-aware queries
                document_indexes = [
                    # Composite index for jurisdiction + document type queries
                    {
                        "name": "idx_documents_jurisdiction_type",
                        "table": "documents",
                        "columns": ["jurisdiction", "document_type"],
                        "sql": """
                        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_jurisdiction_type 
                        ON documents (jurisdiction, document_type)
                        """
                    },
                    # Index for jurisdiction + analysis status
                    {
                        "name": "idx_documents_jurisdiction_status",
                        "table": "documents", 
                        "columns": ["jurisdiction", "analysis_status"],
                        "sql": """
                        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_jurisdiction_status 
                        ON documents (jurisdiction, analysis_status)
                        """
                    },
                    # GIN index for detected_jurisdiction JSON field
                    {
                        "name": "idx_documents_detected_jurisdiction_gin",
                        "table": "documents",
                        "columns": ["detected_jurisdiction"],
                        "sql": """
                        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_detected_jurisdiction_gin 
                        ON documents USING GIN (detected_jurisdiction)
                        """
                    },
                    # Index for user + jurisdiction queries
                    {
                        "name": "idx_documents_user_jurisdiction",
                        "table": "documents",
                        "columns": ["uploaded_by", "jurisdiction"],
                        "sql": """
                        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_user_jurisdiction 
                        ON documents (uploaded_by, jurisdiction)
                        """
                    },
                    # Full-text search index for document content
                    {
                        "name": "idx_documents_content_fts",
                        "table": "documents",
                        "columns": ["content"],
                        "sql": """
                        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_content_fts 
                        ON documents USING GIN (to_tsvector('english', content))
                        """
                    }
                ]
                
                # Analysis results indexes
                analysis_indexes = [
                    # Index for document + analysis type queries
                    {
                        "name": "idx_analysis_document_status",
                        "table": "analysis_results",
                        "columns": ["document_id", "status"],
                        "sql": """
                        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analysis_document_status 
                        ON analysis_results (document_id, status)
                        """
                    },
                    # GIN indexes for JSON fields in analysis results
                    {
                        "name": "idx_analysis_summary_gin",
                        "table": "analysis_results",
                        "columns": ["summary"],
                        "sql": """
                        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analysis_summary_gin 
                        ON analysis_results USING GIN (summary)
                        """
                    },
                    {
                        "name": "idx_analysis_risks_gin",
                        "table": "analysis_results",
                        "columns": ["risks"],
                        "sql": """
                        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analysis_risks_gin 
                        ON analysis_results USING GIN (risks)
                        """
                    }
                ]
                
                # Jurisdiction analysis indexes
                jurisdiction_indexes = [
                    # Composite index for jurisdiction analysis queries
                    {
                        "name": "idx_jurisdiction_analysis_doc_jurisdiction",
                        "table": "jurisdiction_analysis",
                        "columns": ["document_id", "jurisdiction"],
                        "sql": """
                        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_jurisdiction_analysis_doc_jurisdiction 
                        ON jurisdiction_analysis (document_id, jurisdiction)
                        """
                    },
                    # Index for jurisdiction + confidence score
                    {
                        "name": "idx_jurisdiction_analysis_jurisdiction_confidence",
                        "table": "jurisdiction_analysis",
                        "columns": ["jurisdiction", "confidence_score"],
                        "sql": """
                        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_jurisdiction_analysis_jurisdiction_confidence 
                        ON jurisdiction_analysis (jurisdiction, confidence_score DESC)
                        """
                    },
                    # GIN index for analysis results JSON
                    {
                        "name": "idx_jurisdiction_analysis_results_gin",
                        "table": "jurisdiction_analysis",
                        "columns": ["analysis_results"],
                        "sql": """
                        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_jurisdiction_analysis_results_gin 
                        ON jurisdiction_analysis USING GIN (analysis_results)
                        """
                    }
                ]
                
                # User indexes for performance
                user_indexes = [
                    # Index for user role queries
                    {
                        "name": "idx_users_role_active",
                        "table": "users",
                        "columns": ["role", "is_active"],
                        "sql": """
                        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_role_active 
                        ON users (role, is_active)
                        """
                    },
                    # Index for organization queries
                    {
                        "name": "idx_users_organization",
                        "table": "users",
                        "columns": ["organization"],
                        "sql": """
                        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_organization 
                        ON users (organization) WHERE organization IS NOT NULL
                        """
                    }
                ]
                
                all_indexes = document_indexes + analysis_indexes + jurisdiction_indexes + user_indexes
                
                for index_def in all_indexes:
                    try:
                        await session.execute(text(index_def["sql"]))
                        await session.commit()
                        indexes_created.append(index_def["name"])
                        logger.info(f"Created index: {index_def['name']}")
                        
                        # Small delay to prevent overwhelming the database
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        logger.warning(f"Failed to create index {index_def['name']}: {e}")
                        await session.rollback()
                
                return {
                    "status": "completed",
                    "indexes_created": indexes_created,
                    "total_indexes": len(all_indexes),
                    "created_count": len(indexes_created)
                }
                
        except Exception as e:
            logger.error(f"Failed to create jurisdiction indexes: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def analyze_query_performance(self, query: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze query performance using EXPLAIN ANALYZE."""
        try:
            async with AsyncSessionLocal() as session:
                # Execute EXPLAIN ANALYZE
                explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
                
                start_time = time.time()
                result = await session.execute(text(explain_query), params or {})
                execution_time = time.time() - start_time
                
                explain_result = result.fetchone()[0]
                
                # Extract key performance metrics
                plan = explain_result[0]["Plan"]
                
                performance_metrics = {
                    "execution_time_ms": execution_time * 1000,
                    "planning_time_ms": explain_result[0].get("Planning Time", 0),
                    "execution_time_db_ms": explain_result[0].get("Execution Time", 0),
                    "total_cost": plan.get("Total Cost", 0),
                    "rows_returned": plan.get("Actual Rows", 0),
                    "node_type": plan.get("Node Type"),
                    "index_usage": self._extract_index_usage(plan),
                    "buffer_usage": self._extract_buffer_usage(plan)
                }
                
                return {
                    "status": "success",
                    "metrics": performance_metrics,
                    "full_plan": explain_result
                }
                
        except Exception as e:
            logger.error(f"Failed to analyze query performance: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _extract_index_usage(self, plan: Dict[str, Any]) -> List[str]:
        """Extract index usage information from query plan."""
        indexes_used = []
        
        def traverse_plan(node):
            if node.get("Node Type") == "Index Scan":
                index_name = node.get("Index Name")
                if index_name:
                    indexes_used.append(index_name)
            
            # Recursively check child plans
            for child in node.get("Plans", []):
                traverse_plan(child)
        
        traverse_plan(plan)
        return indexes_used
    
    def _extract_buffer_usage(self, plan: Dict[str, Any]) -> Dict[str, int]:
        """Extract buffer usage information from query plan."""
        buffer_info = {
            "shared_hit": 0,
            "shared_read": 0,
            "shared_dirtied": 0,
            "shared_written": 0
        }
        
        def traverse_plan(node):
            for key in buffer_info.keys():
                if key.replace("_", " ").title() in node:
                    buffer_info[key] += node.get(key.replace("_", " ").title(), 0)
            
            # Recursively check child plans
            for child in node.get("Plans", []):
                traverse_plan(child)
        
        traverse_plan(plan)
        return buffer_info
    
    async def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get slow queries from pg_stat_statements if available."""
        try:
            async with AsyncSessionLocal() as session:
                # Check if pg_stat_statements extension is available
                check_extension = """
                SELECT EXISTS (
                    SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'
                )
                """
                
                result = await session.execute(text(check_extension))
                extension_exists = result.scalar()
                
                if not extension_exists:
                    return {"status": "extension_not_available", "queries": []}
                
                # Get slow queries
                slow_queries_sql = """
                SELECT 
                    query,
                    calls,
                    total_exec_time,
                    mean_exec_time,
                    rows,
                    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
                FROM pg_stat_statements
                WHERE mean_exec_time > :threshold
                ORDER BY mean_exec_time DESC
                LIMIT :limit
                """
                
                result = await session.execute(
                    text(slow_queries_sql),
                    {"threshold": self.slow_query_threshold * 1000, "limit": limit}
                )
                
                slow_queries = []
                for row in result:
                    slow_queries.append({
                        "query": row.query,
                        "calls": row.calls,
                        "total_exec_time_ms": row.total_exec_time,
                        "mean_exec_time_ms": row.mean_exec_time,
                        "rows": row.rows,
                        "cache_hit_percent": row.hit_percent or 0
                    })
                
                return {"status": "success", "queries": slow_queries}
                
        except Exception as e:
            logger.error(f"Failed to get slow queries: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def get_connection_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        try:
            pool = engine.pool
            
            stats = {
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalid(),
                "total_connections": pool.size() + pool.overflow(),
                "utilization_percent": (pool.checkedout() / (pool.size() + pool.overflow())) * 100 if (pool.size() + pool.overflow()) > 0 else 0
            }
            
            return {"status": "success", "stats": stats}
            
        except Exception as e:
            logger.error(f"Failed to get connection pool stats: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def optimize_table_statistics(self) -> Dict[str, Any]:
        """Update table statistics for better query planning."""
        try:
            async with AsyncSessionLocal() as session:
                tables = [
                    "documents",
                    "analysis_results", 
                    "jurisdiction_analysis",
                    "users"
                ]
                
                updated_tables = []
                
                for table in tables:
                    try:
                        await session.execute(text(f"ANALYZE {table}"))
                        updated_tables.append(table)
                        logger.info(f"Updated statistics for table: {table}")
                    except Exception as e:
                        logger.warning(f"Failed to update statistics for {table}: {e}")
                
                await session.commit()
                
                return {
                    "status": "completed",
                    "updated_tables": updated_tables,
                    "total_tables": len(tables)
                }
                
        except Exception as e:
            logger.error(f"Failed to optimize table statistics: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def get_database_size_info(self) -> Dict[str, Any]:
        """Get database size and table size information."""
        try:
            async with AsyncSessionLocal() as session:
                # Get database size
                db_size_query = """
                SELECT pg_size_pretty(pg_database_size(current_database())) as database_size
                """
                
                result = await session.execute(text(db_size_query))
                database_size = result.scalar()
                
                # Get table sizes
                table_sizes_query = """
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                """
                
                result = await session.execute(text(table_sizes_query))
                
                table_sizes = []
                for row in result:
                    table_sizes.append({
                        "schema": row.schemaname,
                        "table": row.tablename,
                        "size": row.size,
                        "size_bytes": row.size_bytes
                    })
                
                return {
                    "status": "success",
                    "database_size": database_size,
                    "table_sizes": table_sizes
                }
                
        except Exception as e:
            logger.error(f"Failed to get database size info: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def check_index_usage(self) -> Dict[str, Any]:
        """Check index usage statistics."""
        try:
            async with AsyncSessionLocal() as session:
                index_usage_query = """
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_tup_read,
                    idx_tup_fetch,
                    idx_scan
                FROM pg_stat_user_indexes
                WHERE schemaname = 'public'
                ORDER BY idx_scan DESC
                """
                
                result = await session.execute(text(index_usage_query))
                
                index_stats = []
                for row in result:
                    index_stats.append({
                        "schema": row.schemaname,
                        "table": row.tablename,
                        "index": row.indexname,
                        "tuples_read": row.idx_tup_read,
                        "tuples_fetched": row.idx_tup_fetch,
                        "scans": row.idx_scan
                    })
                
                return {"status": "success", "index_stats": index_stats}
                
        except Exception as e:
            logger.error(f"Failed to check index usage: {e}")
            return {"status": "failed", "error": str(e)}
    
    @asynccontextmanager
    async def query_performance_monitor(self, query_name: str):
        """Context manager to monitor query performance."""
        start_time = time.time()
        
        try:
            yield
        finally:
            execution_time = time.time() - start_time
            
            # Update query statistics
            if query_name not in self.query_stats:
                self.query_stats[query_name] = {
                    "total_calls": 0,
                    "total_time": 0,
                    "avg_time": 0,
                    "max_time": 0,
                    "min_time": float('inf')
                }
            
            stats = self.query_stats[query_name]
            stats["total_calls"] += 1
            stats["total_time"] += execution_time
            stats["avg_time"] = stats["total_time"] / stats["total_calls"]
            stats["max_time"] = max(stats["max_time"], execution_time)
            stats["min_time"] = min(stats["min_time"], execution_time)
            
            # Log slow queries
            if execution_time > self.slow_query_threshold:
                logger.warning(f"Slow query detected: {query_name} took {execution_time:.2f}s")
            
            # Cache query statistics
            await cache_manager.set(
                f"query_stats:{query_name}",
                stats,
                ttl=3600  # 1 hour
            )
    
    async def get_query_statistics(self) -> Dict[str, Any]:
        """Get query performance statistics."""
        return {
            "status": "success",
            "query_stats": self.query_stats,
            "slow_query_threshold": self.slow_query_threshold
        }
    
    async def vacuum_analyze_tables(self) -> Dict[str, Any]:
        """Perform VACUUM ANALYZE on all tables."""
        try:
            async with AsyncSessionLocal() as session:
                tables = [
                    "documents",
                    "analysis_results",
                    "jurisdiction_analysis", 
                    "users"
                ]
                
                processed_tables = []
                
                for table in tables:
                    try:
                        await session.execute(text(f"VACUUM ANALYZE {table}"))
                        processed_tables.append(table)
                        logger.info(f"VACUUM ANALYZE completed for table: {table}")
                    except Exception as e:
                        logger.warning(f"Failed to VACUUM ANALYZE {table}: {e}")
                
                return {
                    "status": "completed",
                    "processed_tables": processed_tables,
                    "total_tables": len(tables)
                }
                
        except Exception as e:
            logger.error(f"Failed to vacuum analyze tables: {e}")
            return {"status": "failed", "error": str(e)}


# Global database optimization service instance
db_optimization_service = DatabaseOptimizationService()