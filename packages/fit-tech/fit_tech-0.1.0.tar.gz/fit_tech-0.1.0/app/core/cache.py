from typing import Any, Optional, Union
import json
import redis
from datetime import timedelta
import os

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_client = redis.Redis.from_url(redis_url, decode_responses=True)

class RedisCache:
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """Получить значение из кэша по ключу"""
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    
    @staticmethod
    async def set(key: str, value: Any, expire: Union[int, timedelta] = None) -> bool:
        """Установить значение в кэш с опциональным временем истечения"""
        serialized = json.dumps(value)
        if expire is not None:
            if isinstance(expire, timedelta):
                expire = int(expire.total_seconds())
            return redis_client.setex(key, expire, serialized)
        return redis_client.set(key, serialized)
    
    @staticmethod
    async def delete(key: str) -> int:
        """Удалить значение из кэша по ключу"""
        return redis_client.delete(key)
    
    @staticmethod
    async def clear_pattern(pattern: str) -> int:
        """Удалить все ключи, соответствующие шаблону"""
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
        return 0