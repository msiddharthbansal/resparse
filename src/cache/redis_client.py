import redis
import json
import hashlib
from typing import Optional, Any
from src.config.settings import settings

class RedisCache:
    def __init__(self) -> None:
        self.client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            db=settings.redis_db,
            decode_responses=True
        )
        self.ttl = settings.cache_ttl
        self.enabled = settings.enable_cache

    def _generate_key(self, prefix: str, data: str) -> str:
        hash_value = hashlib.md5(data.encode()).hexdigest()
        return f"{prefix}:{hash_value}"
    
    def get(self, key: str) -> Optional[Any]:
        if not self.enabled:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        if not self.enabled:
            return False
        
        try:
            serialized = json.dumps(value)
            return self.client.setex(
                key, 
                ttl or self.ttl, 
                serialized
            )
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        if not self.enabled:
            return False
        
        try:
            return self.client.delete(key) > 0
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.enabled:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
        except Exception as e:
            print(f"Cache clear error: {e}")
        return 0
    
    def get_query_cache(self, query: str) -> Optional[Any]:
        key = self._generate_key("query", query)
        return self.get(key)
    
    def set_query_cache(self, query: str, results: Any) -> bool:
        key = self._generate_key("query", query)
        return self.set(key, results)

cache = RedisCache()