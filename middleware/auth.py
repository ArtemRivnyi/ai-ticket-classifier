"""
API Key Authentication Middleware
Handles API key validation, rate limiting per key, and usage tracking
"""

from functools import wraps
from flask import request, jsonify, g
import redis
import os
import hashlib
import secrets
from datetime import datetime, timezone
import logging
from sqlalchemy.orm import Session

from config.settings import get_settings
from database.models import SessionLocal, APIKey, User

logger = logging.getLogger(__name__)

# Redis connection
settings = get_settings()
REDIS_URL = settings.REDIS_URL
ALLOW_PROVIDERLESS = os.getenv("ALLOW_PROVIDERLESS", "false").lower() == "true"

try:
    from config.redis_config import get_redis_client

    redis_client = get_redis_client()
    redis_client.ping()
    logger.info("✓ Redis connection established")
except Exception as e:
    if ALLOW_PROVIDERLESS:
        logger.warning(f"⚠️ Redis not available, running with in-memory key store: {e}")
        redis_client = None
    else:
        logger.error(f"✗ Redis connection failed: {e}")
        redis_client = None

# Tier configurations
TIER_LIMITS = {
    "free": {"requests_per_hour": 50, "requests_per_day": 1000},
    "starter": {"requests_per_hour": 1000, "requests_per_day": 10000},
    "professional": {"requests_per_hour": 10000, "requests_per_day": 100000},
    "enterprise": {"requests_per_hour": -1, "requests_per_day": -1},
}


class APIKeyManager:
    """Manage API keys using Database with Redis Caching"""

    @staticmethod
    def generate_key() -> str:
        """Generate a new API key"""
        return f"atc_{secrets.token_urlsafe(32)}"

    @staticmethod
    def hash_key(key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(key.encode()).hexdigest()

    @staticmethod
    def get_key_data(key: str) -> dict:
        """Get API key data from Redis or DB"""
        # Check for Master API Key first
        master_key = os.getenv("MASTER_API_KEY")
        if master_key and key == master_key:
            return {
                "id": "master",
                "key_hash": "master",
                "user_id": "admin",
                "name": "Master Key",
                "tier": "enterprise",
                "is_active": True,
            }

        key_hash = APIKeyManager.hash_key(key)
        
        # 1. Try Redis
        if redis_client:
            cached_data = redis_client.hgetall(f"api_key:{key_hash}")
            if cached_data:
                # Convert bytes to strings/bools if needed
                return {
                    "id": cached_data.get("id"),
                    "user_id": cached_data.get("user_id"),
                    "tier": cached_data.get("tier"),
                    "is_active": cached_data.get("is_active") == "true",
                    "name": cached_data.get("name")
                }

        # 2. Try Database
        db: Session = SessionLocal()
        try:
            api_key_obj = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()
            
            if api_key_obj:
                data = {
                    "id": str(api_key_obj.id),
                    "user_id": str(api_key_obj.user_id),
                    "tier": api_key_obj.tier,
                    "is_active": api_key_obj.is_active,
                    "name": api_key_obj.name
                }
                
                # Cache in Redis
                if redis_client:
                    redis_data = {k: str(v).lower() if isinstance(v, bool) else str(v) for k, v in data.items()}
                    redis_client.hset(f"api_key:{key_hash}", mapping=redis_data)
                    redis_client.expire(f"api_key:{key_hash}", 300) # Cache for 5 mins
                
                return data
            
            return None
        finally:
            db.close()

    @staticmethod
    def create_key(user_id: str, name: str, tier: str = "free") -> dict:
        """Create a new API key"""
        key = APIKeyManager.generate_key()
        key_hash = APIKeyManager.hash_key(key)
        
        db: Session = SessionLocal()
        try:
            # Ensure user exists (if user_id is int, but here we use string IDs for now? 
            # The User model uses Integer ID. But api/auth.py generates "usr_..." string.
            # We need to reconcile this. 
            # Strategy: Let's change User model to use String ID or map it.
            # For now, let's assume user_id passed here is the Integer ID from the DB.
            # But api/auth.py generates a string.
            # Let's fix api/auth.py to create User in DB and get the Integer ID.
            
            new_key = APIKey(
                key_hash=key_hash,
                user_id=int(user_id), # Assuming user_id is int
                name=name,
                tier=tier,
                is_active=True
            )
            db.add(new_key)
            db.commit()
            db.refresh(new_key)
            
            key_data = {
                "key": key,
                "key_id": str(new_key.id),
                "tier": tier,
                "created_at": new_key.created_at.isoformat(),
                "name": name
            }
            
            # Cache in Redis
            if redis_client:
                redis_data = {
                    "id": str(new_key.id),
                    "user_id": str(user_id),
                    "tier": tier,
                    "is_active": "true",
                    "name": name
                }
                redis_client.hset(f"api_key:{key_hash}", mapping=redis_data)
                redis_client.sadd(f"user_keys:{user_id}", key_hash)
                
            return key_data
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating key: {e}")
            raise e
        finally:
            db.close()

    @staticmethod
    def revoke_key(key_id: str, user_id: str) -> bool:
        """Revoke an API key"""
        db: Session = SessionLocal()
        try:
            key = db.query(APIKey).filter(APIKey.id == int(key_id), APIKey.user_id == int(user_id)).first()
            if key:
                key.is_active = False
                db.commit()
                
                # Update Redis
                if redis_client:
                    redis_client.hset(f"api_key:{key.key_hash}", "is_active", "false")
                
                return True
            return False
        except Exception as e:
            logger.error(f"Error revoking key: {e}")
            return False
        finally:
            db.close()

    @staticmethod
    def list_user_keys(user_id: str) -> list:
        """List all keys for a user"""
        db: Session = SessionLocal()
        try:
            keys = db.query(APIKey).filter(APIKey.user_id == int(user_id)).all()
            return [
                {
                    "id": str(k.id),
                    "name": k.name,
                    "tier": k.tier,
                    "is_active": k.is_active,
                    "created_at": k.created_at.isoformat(),
                    "last_used": k.last_used.isoformat() if k.last_used else None,
                    "requests_count": k.total_requests
                }
                for k in keys
            ]
        finally:
            db.close()

class RateLimiter:
    """Rate limiting per API key"""

    @staticmethod
    def check_rate_limit(user_id: str, tier: str) -> tuple:
        """Check if request is within rate limits"""
        if not redis_client:
            return True, {}

        limits = TIER_LIMITS.get(tier, TIER_LIMITS["free"])

        if limits["requests_per_hour"] == -1:
            return True, {"remaining": "unlimited"}

        hour_key = f"rate_limit:hour:{user_id}"
        hour_count = redis_client.incr(hour_key)

        if hour_count == 1:
            redis_client.expire(hour_key, 3600)

        if hour_count > limits["requests_per_hour"]:
            return False, {
                "limit": limits["requests_per_hour"],
                "remaining": 0,
                "reset_in": redis_client.ttl(hour_key),
            }
        
        return True, {
            "hourly_limit": limits["requests_per_hour"],
            "hourly_remaining": limits["requests_per_hour"] - hour_count,
        }


def require_api_key(f):
    """Decorator to require API key authentication"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return jsonify({"error": "API key required"}), 401

        key_data = APIKeyManager.get_key_data(api_key)

        if not key_data:
            return jsonify({"error": "Invalid API key"}), 401

        if not key_data.get("is_active"):
            return jsonify({"error": "API key revoked"}), 401

        user_id = key_data.get("user_id")
        tier = key_data.get("tier", "free")

        allowed, rate_info = RateLimiter.check_rate_limit(user_id, tier)

        if not allowed:
            return jsonify({
                "error": "Rate limit exceeded",
                "retry_after": rate_info.get("reset_in")
            }), 429

        # Attach context
        g.user_id = user_id
        g.tier = tier
        
        # Also attach to request for compatibility
        request.user_id = user_id
        request.api_key_tier = tier
        request.rate_limit_info = rate_info
        
        # Async update usage stats (fire and forget in Redis, sync to DB later or via background worker)
        # For now, we just update DB directly in a separate thread or just simple increment if performance allows
        # To keep it simple for MVP, we'll skip DB write on every request and rely on Redis counters if needed, 
        # or just write to DB if traffic is low.
        
        return f(*args, **kwargs)

    return decorated_function

def optional_api_key(f):
    """Decorator for optional API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return require_api_key(f)(*args, **kwargs)
        
        # Anonymous fallback
        g.user_id = f"anon:{request.remote_addr}"
        g.tier = "free"
        return f(*args, **kwargs)
    return decorated_function
