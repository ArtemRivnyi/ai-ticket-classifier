import os
import redis
from redis import ConnectionPool


_redis_pool = None
_redis_client = None


def get_redis_pool():
    """Get or create Redis connection pool (singleton)"""
    global _redis_pool
    if _redis_pool is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        _redis_pool = ConnectionPool.from_url(
            redis_url,
            max_connections=20,
            socket_connect_timeout=5,
            socket_keepalive=True,
            health_check_interval=30,
            decode_responses=True,
        )
    return _redis_pool


def get_redis_client():
    """Get Redis client using singleton pool"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(connection_pool=get_redis_pool())
    return _redis_client
