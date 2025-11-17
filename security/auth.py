import secrets
import hashlib
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
import os

class APIKeyManager:
    def __init__(self):
        # In production this will be in database
        self.api_keys = {
            os.getenv('MASTER_API_KEY', 'dev_master_key_change_me'): {
                'tier': 'enterprise',
                'rate_limit': 10000
            }
        }
    
    def generate_key(self, tier='free'):
        """Generate a new API key"""
        key = f"sk_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return key, key_hash
    
    def validate_key(self, api_key):
        """Validate API key"""
        return api_key in self.api_keys
    
    def get_tier(self, api_key):
        """Get user tier"""
        return self.api_keys.get(api_key, {}).get('tier', 'free')

api_key_manager = APIKeyManager()

def require_api_key(f):
    """Decorator to protect endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                'error': 'API key required',
                'message': 'Include X-API-Key header'
            }), 401
        
        if not api_key_manager.validate_key(api_key):
            return jsonify({
                'error': 'Invalid API key',
                'message': 'Check your API key'
            }), 403
        
        # Add tier to request context
        request.user_tier = api_key_manager.get_tier(api_key)
        return f(*args, **kwargs)
    
    return decorated_function
