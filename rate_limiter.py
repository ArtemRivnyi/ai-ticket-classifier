"""
Rate limiting middleware using Redis
"""
import os
import logging
from functools import wraps
from flask import request, jsonify
import redis
from typing import Optional

logger = logging.getLogger(__name__)

class RateLimiter:
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
            logger.info(f"Redis connected successfully: {redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Check if Redis is available"""
        return self.redis_client is not None
    
    def get_client_id(self) -> str:
        """Get client identifier (IP address or API key)"""
        # Prefer API key for identification
        api_key = request.headers.get('X-API-Key', '')
        if api_key:
            return f"key:{api_key[:16]}"  # Use first 16 chars of API key
        
        # Fallback to IP address
        return f"ip:{request.remote_addr}"
    
    def check_rate_limit(
        self, 
        limit: int = 100, 
        window: int = 3600,
        endpoint: Optional[str] = None
    ) -> tuple[bool, dict]:
        """
        Check if request is within rate limit
        
        Args:
            limit: Maximum number of requests
            window: Time window in seconds (default: 1 hour)
            endpoint: Specific endpoint to rate limit (optional)
        
        Returns:
            (is_allowed, info_dict)
        """
        if not self.is_available():
            # If Redis is down, allow request but log warning
            logger.warning("Redis unavailable, rate limiting disabled")
            return True, {"limit": limit, "remaining": limit, "reset": window}
        
        try:
            client_id = self.get_client_id()
            endpoint_suffix = f":{endpoint}" if endpoint else ""
            key = f"ratelimit:{client_id}{endpoint_suffix}"
            
            # Increment counter
            current = self.redis_client.incr(key)
            
            # Set expiry on first request
            if current == 1:
                self.redis_client.expire(key, window)
            
            # Get TTL
            ttl = self.redis_client.ttl(key)
            if ttl == -1:  # Key exists but no expiry set
                self.redis_client.expire(key, window)
                ttl = window
            
            remaining = max(0, limit - current)
            is_allowed = current <= limit
            
            info = {
                "limit": limit,
                "remaining": remaining,
                "reset": ttl,
                "current": current
            }
            
            if not is_allowed:
                logger.warning(f"Rate limit exceeded for {client_id}: {current}/{limit}")
            
            return is_allowed, info
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            # On error, allow request
            return True, {"limit": limit, "remaining": limit, "reset": window}

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(limit: int = 100, window: int = 3600, endpoint: Optional[str] = None):
    """
    Decorator for rate limiting endpoints
    
    Usage:
        @rate_limit(limit=10, window=60)  # 10 requests per minute
        def my_endpoint():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            is_allowed, info = rate_limiter.check_rate_limit(limit, window, endpoint)
            
            # Add rate limit headers to response
            response = None
            if is_allowed:
                response = f(*args, **kwargs)
                if hasattr(response, 'headers'):
                    response.headers['X-RateLimit-Limit'] = str(info['limit'])
                    response.headers['X-RateLimit-Remaining'] = str(info['remaining'])
                    response.headers['X-RateLimit-Reset'] = str(info['reset'])
            else:
                response = jsonify({
                    "error": "Rate limit exceeded",
                    "code": 429,
                    "details": f"Maximum {limit} requests per {window} seconds",
                    "retry_after": info['reset']
                }), 429
                response[0].headers['X-RateLimit-Limit'] = str(info['limit'])
                response[0].headers['X-RateLimit-Remaining'] = str(info['remaining'])
                response[0].headers['X-RateLimit-Reset'] = str(info['reset'])
                response[0].headers['Retry-After'] = str(info['reset'])
            
            return response
        return decorated_function
    return decorator