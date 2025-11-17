"""
JWT Authentication Module
Provides JWT token generation and validation as an alternative to API keys
"""

import os
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)

JWT_SECRET = os.getenv('JWT_SECRET', os.getenv('SECRET_KEY', 'change-this-in-production'))
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))


def generate_jwt_token(user_id: str, tier: str = 'free', email: str = None) -> str:
    """
    Generate a JWT token for a user
    
    Args:
        user_id: User identifier
        tier: User tier (free, starter, professional, enterprise)
        email: User email (optional)
    
    Returns:
        Encoded JWT token
    """
    payload = {
        'user_id': user_id,
        'tier': tier,
        'email': email,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        'type': 'access'
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    logger.info(f"JWT token generated for user {user_id}")
    return token


def validate_jwt_token(token: str) -> dict:
    """
    Validate a JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Check token type
        if payload.get('type') != 'access':
            logger.warning("Invalid token type")
            return None
        
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None


def require_jwt_or_api_key(f):
    """
    Decorator that accepts either JWT token or API key authentication
    
    Usage:
        @app.route('/api/v1/endpoint')
        @require_jwt_or_api_key
        def endpoint():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Try JWT first
        auth_header = request.headers.get('Authorization', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            payload = validate_jwt_token(token)
            
            if payload:
                # Add user info to request context
                request.user_id = payload.get('user_id')
                request.api_key_tier = payload.get('tier', 'free')
                request.auth_type = 'jwt'
                return f(*args, **kwargs)
            else:
                return jsonify({
                    'error': 'Invalid or expired token',
                    'message': 'Please provide a valid JWT token'
                }), 401
        
        # Fallback to API key
        api_key = request.headers.get('X-API-Key')
        if api_key:
            try:
                from middleware.auth import APIKeyManager, RateLimiter
                
                key_data = APIKeyManager.get_key_data(api_key)
                if not key_data or key_data.get('is_active') != 'true':
                    return jsonify({
                        'error': 'Invalid API key',
                        'message': 'The provided API key is invalid or revoked'
                    }), 401
                
                user_id = key_data.get('user_id')
                tier = key_data.get('tier', 'free')
                
                # Check rate limits
                allowed, rate_info = RateLimiter.check_rate_limit(user_id, tier)
                if not allowed:
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'rate_limit': rate_info
                    }), 429
                
                request.user_id = user_id
                request.api_key_tier = tier
                request.rate_limit_info = rate_info
                request.auth_type = 'api_key'
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"API key validation error: {e}")
                return jsonify({'error': 'Authentication failed'}), 401
        
        # No authentication provided
        return jsonify({
            'error': 'Authentication required',
            'message': 'Please provide either a JWT token in Authorization header or an API key in X-API-Key header'
        }), 401
    
    return decorated_function

