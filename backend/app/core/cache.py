"""Redis caching system for analysis results and task management."""

import asyncio
import json
import logging
import hashlib
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import redis.asyncio as redis
from redis.asyncio import Redis

from app.config import get_settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis-based cache manager for analysis results and task data."""
    
    def __init__(self):
        """Initialize Redis connection."""
        settings = get_settings()
        self.redis_client: Optional[Redis] = None
        self.redis_url = settings.redis_url
        self.default_ttl = 3600  # 1 hour default TTL
        self.analysis_ttl = 86400  # 24 hours for analysis results
        self.task_ttl = 7200  # 2 hours for task data
    
    async def connect(self):
        """Establish Redis connection."""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    async def disconnect(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")
    
    def _generate_cache_key(self, prefix: str, identifier: str, **kwargs) -> str:
        """Generate a cache key with optional parameters."""
        key_parts = [prefix, identifier]
        
        if kwargs:
            # Sort kwargs for consistent key generation
            sorted_kwargs = sorted(kwargs.items())
            params_str = json.dumps(sorted_kwargs, sort_keys=True)
            params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
            key_parts.append(params_hash)
        
        return ":".join(key_parts)
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        serialize: bool = True
    ) -> bool:
        """Set a value in cache with optional TTL."""
        if not self.redis_client:
            return False
        
        try:
            if serialize:
                value = json.dumps(value, default=str)
            
            ttl = ttl or self.default_ttl
            await self.redis_client.setex(key, ttl, value)
            return True
            
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {e}")
            return False
    
    async def get(self, key: str, deserialize: bool = True) -> Optional[Any]:
        """Get a value from cache."""
        if not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value is None:
                return None
            
            if deserialize:
                return json.loads(value)
            return value
            
        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.delete(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.exists(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Failed to check cache key {key}: {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key."""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.expire(key, ttl)
            return result
            
        except Exception as e:
            logger.error(f"Failed to set expiration for key {key}: {e}")
            return False
    
    # Analysis result caching methods
    
    async def cache_analysis_result(
        self,
        document_id: str,
        analysis_type: str,
        result: Dict[str, Any],
        jurisdiction: Optional[str] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """Cache analysis result with document and analysis type."""
        cache_key = self._generate_cache_key(
            "analysis",
            document_id,
            type=analysis_type,
            jurisdiction=jurisdiction
        )
        
        cache_data = {
            "document_id": document_id,
            "analysis_type": analysis_type,
            "jurisdiction": jurisdiction,
            "result": result,
            "cached_at": datetime.utcnow().isoformat(),
            "ttl": ttl or self.analysis_ttl
        }
        
        return await self.set(cache_key, cache_data, ttl or self.analysis_ttl)
    
    async def get_cached_analysis_result(
        self,
        document_id: str,
        analysis_type: str,
        jurisdiction: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get cached analysis result."""
        cache_key = self._generate_cache_key(
            "analysis",
            document_id,
            type=analysis_type,
            jurisdiction=jurisdiction
        )
        
        cached_data = await self.get(cache_key)
        if cached_data:
            return cached_data.get("result")
        return None
    
    async def invalidate_document_analysis_cache(self, document_id: str) -> int:
        """Invalidate all cached analysis results for a document."""
        if not self.redis_client:
            return 0
        
        try:
            pattern = f"analysis:{document_id}:*"
            keys = await self.redis_client.keys(pattern)
            
            if keys:
                deleted = await self.redis_client.delete(*keys)
                logger.info(f"Invalidated {deleted} analysis cache entries for document {document_id}")
                return deleted
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to invalidate analysis cache for document {document_id}: {e}")
            return 0
    
    # Task progress and result caching methods
    
    async def cache_task_progress(
        self,
        task_id: str,
        progress: int,
        total: int,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Cache task progress information."""
        cache_key = self._generate_cache_key("task_progress", task_id)
        
        progress_data = {
            "task_id": task_id,
            "progress": progress,
            "total": total,
            "percentage": int((progress / total) * 100) if total > 0 else 0,
            "message": message,
            "metadata": metadata or {},
            "updated_at": datetime.utcnow().isoformat()
        }
        
        return await self.set(cache_key, progress_data, self.task_ttl)
    
    async def get_task_progress(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get cached task progress."""
        cache_key = self._generate_cache_key("task_progress", task_id)
        return await self.get(cache_key)
    
    async def cache_task_result(
        self,
        task_id: str,
        result: Dict[str, Any],
        status: str = "completed",
        ttl: Optional[int] = None
    ) -> bool:
        """Cache task result."""
        cache_key = self._generate_cache_key("task_result", task_id)
        
        result_data = {
            "task_id": task_id,
            "status": status,
            "result": result,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        return await self.set(cache_key, result_data, ttl or self.task_ttl)
    
    async def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get cached task result."""
        cache_key = self._generate_cache_key("task_result", task_id)
        return await self.get(cache_key)
    
    async def delete_task_cache(self, task_id: str) -> int:
        """Delete all cached data for a task."""
        if not self.redis_client:
            return 0
        
        try:
            keys_to_delete = [
                self._generate_cache_key("task_progress", task_id),
                self._generate_cache_key("task_result", task_id)
            ]
            
            deleted = await self.redis_client.delete(*keys_to_delete)
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to delete task cache for {task_id}: {e}")
            return 0
    
    # Document content caching methods
    
    async def cache_document_content(
        self,
        document_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """Cache document content for quick access."""
        cache_key = self._generate_cache_key("document", document_id)
        
        document_data = {
            "document_id": document_id,
            "content": content,
            "metadata": metadata or {},
            "cached_at": datetime.utcnow().isoformat()
        }
        
        return await self.set(cache_key, document_data, ttl or self.analysis_ttl)
    
    async def get_cached_document_content(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get cached document content."""
        cache_key = self._generate_cache_key("document", document_id)
        return await self.get(cache_key)
    
    # Session and user data caching methods
    
    async def cache_user_session(
        self,
        session_id: str,
        user_id: str,
        session_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Cache user session data."""
        cache_key = self._generate_cache_key("session", session_id)
        
        session_info = {
            "session_id": session_id,
            "user_id": user_id,
            "data": session_data,
            "created_at": datetime.utcnow().isoformat()
        }
        
        return await self.set(cache_key, session_info, ttl or 7200)  # 2 hours for sessions
    
    async def get_user_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get cached user session data."""
        cache_key = self._generate_cache_key("session", session_id)
        return await self.get(cache_key)
    
    async def delete_user_session(self, session_id: str) -> bool:
        """Delete user session from cache."""
        cache_key = self._generate_cache_key("session", session_id)
        return await self.delete(cache_key)
    
    # Batch operations
    
    async def get_multiple(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache."""
        if not self.redis_client or not keys:
            return {}
        
        try:
            values = await self.redis_client.mget(keys)
            result = {}
            
            for key, value in zip(keys, values):
                if value is not None:
                    try:
                        result[key] = json.loads(value)
                    except json.JSONDecodeError:
                        result[key] = value
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get multiple cache keys: {e}")
            return {}
    
    async def set_multiple(
        self, 
        data: Dict[str, Any], 
        ttl: Optional[int] = None,
        serialize: bool = True
    ) -> bool:
        """Set multiple values in cache."""
        if not self.redis_client or not data:
            return False
        
        try:
            pipe = self.redis_client.pipeline()
            
            for key, value in data.items():
                if serialize:
                    value = json.dumps(value, default=str)
                
                pipe.setex(key, ttl or self.default_ttl, value)
            
            await pipe.execute()
            return True
            
        except Exception as e:
            logger.error(f"Failed to set multiple cache keys: {e}")
            return False
    
    # Cache statistics and management
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.redis_client:
            return {"error": "Redis not connected"}
        
        try:
            info = await self.redis_client.info()
            
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"error": str(e)}
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate."""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)
    
    async def clear_expired_keys(self) -> int:
        """Clear expired keys (Redis handles this automatically, but useful for monitoring)."""
        if not self.redis_client:
            return 0
        
        try:
            # Get database size before and after
            size_before = await self.redis_client.dbsize()
            
            # Force expire check (Redis does this automatically)
            await self.redis_client.execute_command("EXPIRE", "dummy_key", 0)
            
            size_after = await self.redis_client.dbsize()
            
            return max(0, size_before - size_after)
            
        except Exception as e:
            logger.error(f"Failed to clear expired keys: {e}")
            return 0
    
    # Cache warming methods
    
    async def warm_jurisdiction_cache(
        self,
        jurisdiction: str,
        document_types: List[str],
        analysis_types: List[str]
    ) -> Dict[str, int]:
        """Warm cache with frequently accessed jurisdiction-specific data."""
        if not self.redis_client:
            return {"error": "Redis not connected"}
        
        warmed_count = 0
        failed_count = 0
        
        try:
            # Warm jurisdiction-specific templates and references
            jurisdiction_data = await self._get_jurisdiction_reference_data(jurisdiction)
            
            for doc_type in document_types:
                for analysis_type in analysis_types:
                    cache_key = self._generate_cache_key(
                        "jurisdiction_template",
                        jurisdiction,
                        doc_type=doc_type,
                        analysis_type=analysis_type
                    )
                    
                    template_data = jurisdiction_data.get(f"{doc_type}_{analysis_type}")
                    if template_data:
                        success = await self.set(cache_key, template_data, ttl=86400)  # 24 hours
                        if success:
                            warmed_count += 1
                        else:
                            failed_count += 1
            
            logger.info(f"Cache warming completed: {warmed_count} entries warmed, {failed_count} failed")
            
            return {
                "warmed": warmed_count,
                "failed": failed_count,
                "jurisdiction": jurisdiction
            }
            
        except Exception as e:
            logger.error(f"Failed to warm jurisdiction cache: {e}")
            return {"error": str(e)}
    
    async def _get_jurisdiction_reference_data(self, jurisdiction: str) -> Dict[str, Any]:
        """Get reference data for jurisdiction cache warming."""
        # This would typically fetch from a database or external service
        # For now, return sample data structure
        reference_data = {}
        
        if jurisdiction == "IN":
            reference_data.update({
                "contract_comprehensive": {
                    "acts": ["Indian Contract Act 1872", "Specific Relief Act 1963"],
                    "stamp_duty_rates": {"Maharashtra": 0.1, "Delhi": 0.05},
                    "registration_requirements": ["Notarization", "Registration"]
                },
                "agreement_risk_analysis": {
                    "common_risks": ["Stamp duty non-compliance", "Registration issues"],
                    "compliance_checklist": ["GST implications", "Foreign exchange regulations"]
                }
            })
        elif jurisdiction == "US":
            reference_data.update({
                "contract_comprehensive": {
                    "regulations": ["UCC Article 2", "Federal Trade Commission Act"],
                    "state_variations": {"CA": "CCPA compliance", "NY": "Martin Act"},
                    "federal_requirements": ["Securities regulations", "Antitrust laws"]
                },
                "agreement_risk_analysis": {
                    "common_risks": ["State law conflicts", "Federal preemption"],
                    "compliance_checklist": ["Securities compliance", "Privacy laws"]
                }
            })
        
        return reference_data
    
    async def warm_frequently_accessed_data(self) -> Dict[str, int]:
        """Warm cache with frequently accessed analysis data."""
        if not self.redis_client:
            return {"error": "Redis not connected"}
        
        warmed_count = 0
        
        try:
            # Common legal terms and definitions
            legal_terms = await self._get_common_legal_terms()
            for term, definition in legal_terms.items():
                cache_key = self._generate_cache_key("legal_term", term)
                success = await self.set(cache_key, definition, ttl=604800)  # 7 days
                if success:
                    warmed_count += 1
            
            # Jurisdiction detection patterns
            detection_patterns = await self._get_jurisdiction_detection_patterns()
            for jurisdiction, patterns in detection_patterns.items():
                cache_key = self._generate_cache_key("detection_patterns", jurisdiction)
                success = await self.set(cache_key, patterns, ttl=86400)  # 24 hours
                if success:
                    warmed_count += 1
            
            logger.info(f"Warmed {warmed_count} frequently accessed cache entries")
            
            return {"warmed": warmed_count}
            
        except Exception as e:
            logger.error(f"Failed to warm frequently accessed data: {e}")
            return {"error": str(e)}
    
    async def _get_common_legal_terms(self) -> Dict[str, str]:
        """Get common legal terms for cache warming."""
        return {
            "force_majeure": "Unforeseeable circumstances that prevent a party from fulfilling a contract",
            "indemnification": "Security or protection against a loss or other financial burden",
            "liquidated_damages": "A predetermined amount of money that must be paid as damages",
            "material_adverse_change": "A change that significantly affects the business or financial condition",
            "representations_warranties": "Statements of fact and promises about the current state of affairs"
        }
    
    async def _get_jurisdiction_detection_patterns(self) -> Dict[str, List[str]]:
        """Get jurisdiction detection patterns for cache warming."""
        return {
            "IN": [
                "Indian Contract Act", "Companies Act", "GST", "rupees", "lakhs", "crores",
                "Supreme Court of India", "High Court", "District Court", "SEBI", "RBI"
            ],
            "US": [
                "USC", "CFR", "UCC", "dollars", "Federal Court", "District Court",
                "SEC", "FTC", "Supreme Court of the United States", "Circuit Court"
            ]
        }
    
    # Enhanced jurisdiction-specific caching methods
    
    async def cache_jurisdiction_analysis_batch(
        self,
        analyses: List[Dict[str, Any]],
        ttl: Optional[int] = None
    ) -> Dict[str, int]:
        """Cache multiple jurisdiction-specific analyses in batch."""
        if not self.redis_client or not analyses:
            return {"cached": 0, "failed": 0}
        
        cached_count = 0
        failed_count = 0
        
        try:
            pipe = self.redis_client.pipeline()
            
            for analysis in analyses:
                document_id = analysis.get("document_id")
                analysis_type = analysis.get("analysis_type")
                jurisdiction = analysis.get("jurisdiction")
                result = analysis.get("result")
                
                if all([document_id, analysis_type, result]):
                    cache_key = self._generate_cache_key(
                        "analysis",
                        document_id,
                        type=analysis_type,
                        jurisdiction=jurisdiction
                    )
                    
                    cache_data = {
                        "document_id": document_id,
                        "analysis_type": analysis_type,
                        "jurisdiction": jurisdiction,
                        "result": result,
                        "cached_at": datetime.utcnow().isoformat(),
                        "ttl": ttl or self.analysis_ttl
                    }
                    
                    serialized_data = json.dumps(cache_data, default=str)
                    pipe.setex(cache_key, ttl or self.analysis_ttl, serialized_data)
                    cached_count += 1
                else:
                    failed_count += 1
            
            await pipe.execute()
            
            logger.info(f"Batch cached {cached_count} analyses, {failed_count} failed")
            
            return {"cached": cached_count, "failed": failed_count}
            
        except Exception as e:
            logger.error(f"Failed to batch cache analyses: {e}")
            return {"cached": 0, "failed": len(analyses)}
    
    async def get_jurisdiction_cache_stats(self, jurisdiction: str) -> Dict[str, Any]:
        """Get cache statistics for a specific jurisdiction."""
        if not self.redis_client:
            return {"error": "Redis not connected"}
        
        try:
            # Count keys for this jurisdiction
            analysis_pattern = f"analysis:*:*jurisdiction*{jurisdiction}*"
            template_pattern = f"jurisdiction_template:{jurisdiction}:*"
            
            analysis_keys = await self.redis_client.keys(analysis_pattern)
            template_keys = await self.redis_client.keys(template_pattern)
            
            return {
                "jurisdiction": jurisdiction,
                "analysis_cache_count": len(analysis_keys),
                "template_cache_count": len(template_keys),
                "total_keys": len(analysis_keys) + len(template_keys)
            }
            
        except Exception as e:
            logger.error(f"Failed to get jurisdiction cache stats: {e}")
            return {"error": str(e)}
    
    async def invalidate_jurisdiction_cache(self, jurisdiction: str) -> int:
        """Invalidate all cached data for a specific jurisdiction."""
        if not self.redis_client:
            return 0
        
        try:
            patterns = [
                f"analysis:*:*jurisdiction*{jurisdiction}*",
                f"jurisdiction_template:{jurisdiction}:*",
                f"detection_patterns:{jurisdiction}"
            ]
            
            total_deleted = 0
            
            for pattern in patterns:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    deleted = await self.redis_client.delete(*keys)
                    total_deleted += deleted
            
            logger.info(f"Invalidated {total_deleted} cache entries for jurisdiction {jurisdiction}")
            
            return total_deleted
            
        except Exception as e:
            logger.error(f"Failed to invalidate jurisdiction cache: {e}")
            return 0


# Global cache manager instance
cache_manager = CacheManager()


# Utility functions for common caching patterns

async def get_or_set_cache(
    key: str,
    fetch_function,
    ttl: Optional[int] = None,
    *args,
    **kwargs
) -> Any:
    """Get value from cache or fetch and cache it."""
    # Try to get from cache first
    cached_value = await cache_manager.get(key)
    if cached_value is not None:
        return cached_value
    
    # Fetch the value
    try:
        if asyncio.iscoroutinefunction(fetch_function):
            value = await fetch_function(*args, **kwargs)
        else:
            value = fetch_function(*args, **kwargs)
        
        # Cache the value
        await cache_manager.set(key, value, ttl)
        return value
        
    except Exception as e:
        logger.error(f"Failed to fetch and cache value for key {key}: {e}")
        return None


async def cache_analysis_if_not_exists(
    document_id: str,
    analysis_type: str,
    analysis_function,
    jurisdiction: Optional[str] = None,
    ttl: Optional[int] = None,
    *args,
    **kwargs
) -> Optional[Dict[str, Any]]:
    """Cache analysis result if it doesn't exist."""
    # Check if already cached
    cached_result = await cache_manager.get_cached_analysis_result(
        document_id, analysis_type, jurisdiction
    )
    
    if cached_result:
        logger.info(f"Using cached {analysis_type} analysis for document {document_id}")
        return cached_result
    
    # Perform analysis and cache result
    try:
        if asyncio.iscoroutinefunction(analysis_function):
            result = await analysis_function(*args, **kwargs)
        else:
            result = analysis_function(*args, **kwargs)
        
        # Cache the result
        await cache_manager.cache_analysis_result(
            document_id, analysis_type, result, jurisdiction, ttl
        )
        
        logger.info(f"Cached {analysis_type} analysis for document {document_id}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to perform and cache {analysis_type} analysis: {e}")
        return None