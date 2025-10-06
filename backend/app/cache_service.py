import redis
import json
import logging
from typing import Optional, Any, Dict, List
from datetime import datetime, timedelta
from .core.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    """Redis-based caching service for high-performance data storage"""
    
    def __init__(self):
        self.redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379')
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Redis cache connected successfully")
        except Exception as e:
            logger.warning(f"⚠️ Redis not available, using in-memory fallback: {e}")
            self.redis_client = None
            self._fallback_cache = {}
    
    def _get_fallback(self, key: str) -> Optional[Any]:
        """Get value from fallback cache if Redis is not available"""
        if key in self._fallback_cache:
            data, expiry = self._fallback_cache[key]
            if datetime.utcnow() < expiry:
                return data
            else:
                del self._fallback_cache[key]
        return None
    
    def _set_fallback(self, key: str, value: Any, ttl: int):
        """Set value in fallback cache if Redis is not available"""
        expiry = datetime.utcnow() + timedelta(seconds=ttl)
        self._fallback_cache[key] = (value, expiry)
        
        # Clean up expired entries
        current_time = datetime.utcnow()
        expired_keys = [k for k, (_, exp) in self._fallback_cache.items() if current_time >= exp]
        for k in expired_keys:
            del self._fallback_cache[k]
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                return json.loads(value) if value else None
            else:
                return self._get_fallback(key)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL"""
        try:
            if self.redis_client:
                serialized = json.dumps(value, default=str)
                return self.redis_client.setex(key, ttl, serialized)
            else:
                self._set_fallback(key, value, ttl)
                return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if self.redis_client:
                return bool(self.redis_client.delete(key))
            else:
                if key in self._fallback_cache:
                    del self._fallback_cache[key]
                return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            if self.redis_client:
                return bool(self.redis_client.exists(key))
            else:
                return key in self._fallback_cache
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache"""
        result = {}
        for key in keys:
            value = await self.get(key)
            if value is not None:
                result[key] = value
        return result
    
    async def set_many(self, data: Dict[str, Any], ttl: int = 300) -> bool:
        """Set multiple values in cache"""
        try:
            if self.redis_client:
                pipe = self.redis_client.pipeline()
                for key, value in data.items():
                    serialized = json.dumps(value, default=str)
                    pipe.setex(key, ttl, serialized)
                pipe.execute()
                return True
            else:
                for key, value in data.items():
                    self._set_fallback(key, value, ttl)
                return True
        except Exception as e:
            logger.error(f"Cache set_many error: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
                return 0
            else:
                # For fallback cache, we can't do pattern matching efficiently
                # Just clear all entries
                self._fallback_cache.clear()
                return len(self._fallback_cache)
        except Exception as e:
            logger.error(f"Cache clear_pattern error for pattern {pattern}: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if self.redis_client:
                info = self.redis_client.info()
                return {
                    "connected": True,
                    "used_memory": info.get("used_memory_human", "0B"),
                    "connected_clients": info.get("connected_clients", 0),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0),
                    "total_keys": self.redis_client.dbsize()
                }
            else:
                return {
                    "connected": False,
                    "fallback_entries": len(self._fallback_cache),
                    "mode": "fallback"
                }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"connected": False, "error": str(e)}

# Global cache instance
cache_service = CacheService()
