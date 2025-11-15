"""
API Key Authentication Middleware
Handles API key validation, rate limiting per key, and usage tracking
"""

from functools import wraps
from flask import request, jsonify
import redis
import os
import hashlib
import secrets
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Redis connection
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    logger.info("✓ Redis connection established")
except Exception as e:
    logger.error(f"✗ Redis connection failed: {e}")
    redis_client = None

# Tier configurations
TIER_LIMITS = {
    'free': {
        'requests_per_hour': 100,
        'requests_per_day': 1000,
        'batch_size': 10
    },
    'starter': {
        'requests_per_hour': 1000,
        'requests_per_day': 10000,
        'batch_size': 50
    },
    'professional': {
        'requests_per_hour': 10000,
        'requests_per_day': 100000,
        'batch_size': 100
    },
    'enterprise': {
        'requests_per_hour': -1,
        'requests_per_day': -1,
        'batch_size': 1000
    }
}

class APIKeyManager:
    """Manage API keys in Redis"""
    
    @staticmethod
    def generate_key() -> str:
        """Generate a new API key"""
        return f"atc_{secrets.token_urlsafe(32)}"
    
    @staticmethod
    def hash_key(key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    @staticmethod
    def create_key(user_id: str, name: str, tier: str = 'free') -> dict:
        """Create a new API key"""
        if not redis_client:
            raise Exception("Redis not available")
        
        key = APIKeyManager.generate_key()
        key_hash = APIKeyManager.hash_key(key)
        key_id = secrets.token_urlsafe(16)
        
        key_data = {
            'id': key_id,
            'key_hash': key_hash,
            'user_id': user_id,
            'name': name,
            'tier': tier,
            'is_active': 'true',
            'created_at': datetime.utcnow().isoformat(),
            'last_used': '',
            'requests_count': '0',
            'rate_limit': str(TIER_LIMITS[tier]['requests_per_hour'])
        }
        
        redis_client.hset(f"api_key:{key_hash}", mapping=key_data)
        redis_client.sadd(f"user_keys:{user_id}", key_hash)
        
        logger.info(f"Created API key {key_id} for user {user_id}")
        
        return {
            'key': key,
            'key_id': key_id,
            'tier': tier,
            'created_at': key_data['created_at']
        }
    
    @staticmethod
    def get_key_data(key: str) -> dict:
        """Get API key data"""
        if not redis_client:
            return None
        
        key_hash = APIKeyManager.hash_key(key)
        data = redis_client.hgetall(f"api_key:{key_hash}")
        
        return data if data else None
    
    @staticmethod
    def revoke_key(key_id: str, user_id: str) -> bool:
        """Revoke an API key"""
        if not redis_client:
            return False
        
        user_keys = redis_client.smembers(f"user_keys:{user_id}")
        
        for key_hash in user_keys:
            key_data = redis_client.hgetall(f"api_key:{key_hash}")
            if key_data.get('id') == key_id:
                redis_client.hset(f"api_key:{key_hash}", 'is_active', 'false')
                logger.info(f"Revoked API key {key_id}")
                return True
        
        return False
    
    @staticmethod
    def list_user_keys(user_id: str) -> list:
        """List all keys for a user"""
        if not redis_client:
            return []
        
        user_keys = redis_client.smembers(f"user_keys:{user_id}")
        keys_data = []
        
        for key_hash in user_keys:
            data = redis_client.hgetall(f"api_key:{key_hash}")
            if data:
                keys_data.append({
                    'id': data.get('id'),
                    'name': data.get('name'),
                    'tier': data.get('tier'),
                    'is_active': data.get('is_active') == 'true',
                    'created_at': data.get('created_at'),
                    'last_used': data.get('last_used'),
                    'requests_count': int(data.get('requests_count', 0))
                })
        
        return keys_data

class RateLimiter:
    """Rate limiting per API key"""
    
    @staticmethod
    def check_rate_limit(user_id: str, tier: str) -> tuple:
        """Check if request is within rate limits"""
        if not redis_client:
            return True, {}
        
        limits = TIER_LIMITS.get(tier, TIER_LIMITS['free'])
        
        if limits['requests_per_hour'] == -1:
            return True, {'remaining': 'unlimited'}
        
        hour_key = f"rate_limit:hour:{user_id}"
        hour_count = redis_client.incr(hour_key)
        
        if hour_count == 1:
            redis_client.expire(hour_key, 3600)
        
        if hour_count > limits['requests_per_hour']:
            return False, {
                'limit': limits['requests_per_hour'],
                'remaining': 0,
                'reset_in': redis_client.ttl(hour_key)
            }
        
        day_key = f"rate_limit:day:{user_id}"
        day_count = redis_client.incr(day_key)
        
        if day_count == 1:
            redis_client.expire(day_key, 86400)
        
        if day_count > limits['requests_per_day']:
            return False, {
                'limit': limits['requests_per_day'],
                'remaining': 0,
                'reset_in': redis_client.ttl(day_key)
            }
        
        return True, {
            'hourly_limit': limits['requests_per_hour'],
            'hourly_remaining': limits['requests_per_hour'] - hour_count,
            'daily_limit': limits['requests_per_day'],
            'daily_remaining': limits['requests_per_day'] - day_count
        }

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                'error': 'API key required',
                'message': 'Please provide an API key in X-API-Key header'
            }), 401
        
        key_data = APIKeyManager.get_key_data(api_key)
        
        if not key_data:
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is invalid'
            }), 401
        
        if key_data.get('is_active') != 'true':
            return jsonify({
                'error': 'API key revoked',
                'message': 'This API key has been revoked'
            }), 401
        
        user_id = key_data.get('user_id')
        tier = key_data.get('tier', 'free')
        
        allowed, rate_info = RateLimiter.check_rate_limit(user_id, tier)
        
        if not allowed:
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': f'You have exceeded your rate limit. Resets in {rate_info["reset_in"]} seconds',
                'rate_limit': rate_info
            }), 429
        
        if redis_client:
            key_hash = APIKeyManager.hash_key(api_key)
            redis_client.hset(f"api_key:{key_hash}", 'last_used', datetime.utcnow().isoformat())
            redis_client.hincrby(f"api_key:{key_hash}", 'requests_count', 1)
        
        request.user_id = user_id
        request.api_key_tier = tier
        request.rate_limit_info = rate_info
        
        response = f(*args, **kwargs)
        
        if isinstance(response, tuple):
            resp_obj = response[0]
        else:
            resp_obj = response
        
        if hasattr(resp_obj, 'headers') and rate_info.get('hourly_limit'):
            resp_obj.headers['X-RateLimit-Limit'] = str(rate_info['hourly_limit'])
            resp_obj.headers['X-RateLimit-Remaining'] = str(rate_info['hourly_remaining'])
        
        return response
    
    return decorated_function

def optional_api_key(f):
    """Decorator for optional API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if api_key:
            return require_api_key(f)(*args, **kwargs)
        else:
            ip = request.remote_addr
            request.user_id = f"anonymous:{ip}"
            request.api_key_tier = 'anonymous'
            
            if redis_client:
                ip_key = f"rate_limit:ip:{ip}"
                ip_count = redis_client.incr(ip_key)
                
                if ip_count == 1:
                    redis_client.expire(ip_key, 3600)
                
                if ip_count > 10:
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'message': 'Anonymous rate limit exceeded. Please use an API key.'
                    }), 429
            
            return f(*args, **kwargs)
    
    return decorated_function
