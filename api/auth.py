"""
Authentication and API Key Management Endpoints
"""

from flask import Blueprint, request, jsonify
from pydantic import BaseModel, EmailStr, Field, ValidationError
import secrets
import logging

# Импортируем после создания middleware
try:
    from middleware.auth import APIKeyManager, require_api_key
except ImportError:
    APIKeyManager = None
    require_api_key = lambda f: f

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

class UserRegistration(BaseModel):
    email: EmailStr = Field(..., description="User email")
    organization: str = Field(..., min_length=2, max_length=100)
    name: str = Field(..., min_length=2, max_length=100)

class CreateAPIKey(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user and get their first API key"""
    try:
        data = UserRegistration(**request.json)
        user_id = f"usr_{secrets.token_urlsafe(16)}"
        
        if not APIKeyManager:
            return jsonify({'error': 'API Key system not available'}), 500
        
        api_key = APIKeyManager.create_key(
            user_id=user_id,
            name="Default Key",
            tier='free'
        )
        
        logger.info(f"New user registered: {user_id} ({data.email})")
        
        return jsonify({
            'user_id': user_id,
            'email': data.email,
            'organization': data.organization,
            'name': data.name,
            'api_key': api_key,
            'tier': 'free',
            'limits': {
                'requests_per_hour': 100,
                'requests_per_day': 1000,
                'batch_size': 10
            },
            'message': 'Registration successful! Save your API key - it will only be shown once.'
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors()}), 400
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@auth_bp.route('/keys', methods=['GET'])
@require_api_key
def list_keys():
    """List all API keys for current user"""
    try:
        user_id = request.user_id
        keys = APIKeyManager.list_user_keys(user_id)
        
        return jsonify({
            'keys': keys,
            'total': len(keys)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing keys: {e}")
        return jsonify({'error': 'Failed to list keys'}), 500

@auth_bp.route('/keys', methods=['POST'])
@require_api_key
def create_key():
    """Create a new API key"""
    try:
        data = CreateAPIKey(**request.json)
        user_id = request.user_id
        tier = request.api_key_tier
        
        api_key = APIKeyManager.create_key(
            user_id=user_id,
            name=data.name,
            tier=tier
        )
        
        logger.info(f"New API key created for user {user_id}")
        
        return jsonify({
            **api_key,
            'message': 'API key created successfully. Save it - it will only be shown once.'
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors()}), 400
    except Exception as e:
        logger.error(f"Error creating key: {e}")
        return jsonify({'error': 'Failed to create key'}), 500

@auth_bp.route('/keys/<string:key_id>', methods=['DELETE'])
@require_api_key
def revoke_key(key_id):
    """Revoke an API key"""
    try:
        user_id = request.user_id
        success = APIKeyManager.revoke_key(key_id, user_id)
        
        if success:
            logger.info(f"API key {key_id} revoked by user {user_id}")
            return jsonify({'message': 'API key revoked successfully'}), 200
        else:
            return jsonify({'error': 'API key not found'}), 404
            
    except Exception as e:
        logger.error(f"Error revoking key: {e}")
        return jsonify({'error': 'Failed to revoke key'}), 500

@auth_bp.route('/usage', methods=['GET'])
@require_api_key
def usage():
    """Get current usage statistics"""
    try:
        return jsonify({
            'tier': request.api_key_tier,
            'rate_limits': request.rate_limit_info
        }), 200
    except Exception as e:
        logger.error(f"Error getting usage: {e}")
        return jsonify({'error': 'Failed to get usage'}), 500
