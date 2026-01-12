import os
import redis
from redis import ConnectionPool

def get_redis_pool():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    pool = ConnectionPool.from_url(
        redis_url,
        max_connections=10,
        socket_connect_timeout=5,
        socket_keepalive=True,
        health_check_interval=30
    )
    return pool

def get_redis_client():
    pool = get_redis_pool()
    return redis.Redis(connection_pool=pool)
