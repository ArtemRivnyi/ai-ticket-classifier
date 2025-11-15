"""
Redis caching for classification results
"""
import os
import json
import hashlib
import logging
from typing import Optional, Any
import redis

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        try:
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            self.enabled = True
            logger.info(f"Cache connected successfully: {redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis for caching: {e}")
            self.redis_client = None
            self.enabled = False
    
    def _generate_key(self, ticket_text: str, prefix: str = "cache") -> str:
        """Generate cache key from ticket text"""
        # Normalize text: lowercase, strip whitespace
        normalized = ticket_text.lower().strip()
        # Create hash
        text_hash = hashlib.sha256(normalized.encode()).hexdigest()[:16]
        return f"{prefix}:ticket:{text_hash}"
    
    def get(self, ticket_text: str) -> Optional[dict]:
        """
        Get cached classification result
        
        Returns:
            dict or None if not cached
        """
        if not self.enabled:
            return None
        
        try:
            key = self._generate_key(ticket_text)
            cached = self.redis_client.get(key)
            
            if cached:
                logger.info(f"Cache HIT for key: {key}")
                return json.loads(cached)
            else:
                logger.info(f"Cache MISS for key: {key}")
                return None
                
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(
        self, 
        ticket_text: str, 
        classification_result: dict, 
        ttl: int = 3600
    ) -> bool:
        """
        Cache classification result
        
        Args:
            ticket_text: Original ticket text
            classification_result: Classification result to cache
            ttl: Time to live in seconds (default: 1 hour)
        
        Returns:
            bool: Success status
        """
        if not self.enabled:
            return False
        
        try:
            key = self._generate_key(ticket_text)
            value = json.dumps(classification_result)
            
            self.redis_client.setex(key, ttl, value)
            logger.info(f"Cached result for key: {key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, ticket_text: str) -> bool:
        """Delete cached result"""
        if not self.enabled:
            return False
        
        try:
            key = self._generate_key(ticket_text)
            deleted = self.redis_client.delete(key)
            logger.info(f"Deleted cache for key: {key}")
            return bool(deleted)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear_all(self, pattern: str = "cache:ticket:*") -> int:
        """
        Clear all cached results matching pattern
        
        Returns:
            int: Number of keys deleted
        """
        if not self.enabled:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Cleared {deleted} cache entries")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.enabled:
            return {
                "enabled": False,
                "status": "unavailable"
            }
        
        try:
            info = self.redis_client.info('stats')
            keys_count = len(self.redis_client.keys("cache:ticket:*"))
            
            return {
                "enabled": True,
                "status": "connected",
                "total_keys": keys_count,
                "keyspace_hits": info.get('keyspace_hits', 0),
                "keyspace_misses": info.get('keyspace_misses', 0)
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {
                "enabled": False,
                "status": "error",
                "error": str(e)
            }

# Global cache instance
cache_manager = CacheManager()