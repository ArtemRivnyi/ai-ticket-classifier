"""
Comprehensive tests for security/jwt_auth.py
Tests JWT token generation, validation, and decorator
"""
import pytest
import time
from datetime import timedelta
from security.jwt_auth import (
    generate_jwt_token, 
    validate_jwt_token, 
    require_jwt_or_api_key,
    JWT_SECRET,
    JWT_ALGORITHM
)
from flask import Flask, request
from app import app
import jwt

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_generate_jwt_token():
    """Test JWT token generation"""
    token = generate_jwt_token('user123', 'free', 'test@example.com')
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0

def test_generate_jwt_token_without_email():
    """Test JWT token generation without email"""
    token = generate_jwt_token('user123', 'professional')
    assert token is not None
    
    # Decode and verify
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert payload['user_id'] == 'user123'
    assert payload['tier'] == 'professional'
    assert payload.get('email') is None

def test_generate_jwt_token_with_email():
    """Test JWT token generation with email"""
    token = generate_jwt_token('user123', 'free', 'test@example.com')
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert payload['email'] == 'test@example.com'

def test_validate_jwt_token_valid():
    """Test validating a valid JWT token"""
    token = generate_jwt_token('user123', 'free', 'test@example.com')
    payload = validate_jwt_token(token)
    assert payload is not None
    assert payload['user_id'] == 'user123'
    assert payload['tier'] == 'free'

def test_validate_jwt_token_invalid():
    """Test validating an invalid JWT token"""
    invalid_token = 'invalid.token.here'
    payload = validate_jwt_token(invalid_token)
    assert payload is None

def test_validate_jwt_token_expired():
    """Test validating an expired JWT token"""
    # Create expired token manually
    payload = {
        'user_id': 'user123',
        'tier': 'free',
        'iat': time.time() - 100000,  # Very old
        'exp': time.time() - 50000,   # Expired
        'type': 'access'
    }
    expired_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    result = validate_jwt_token(expired_token)
    assert result is None

def test_validate_jwt_token_wrong_type():
    """Test validating token with wrong type"""
    payload = {
        'user_id': 'user123',
        'tier': 'free',
        'iat': time.time(),
        'exp': time.time() + 3600,
        'type': 'refresh'  # Wrong type
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    result = validate_jwt_token(token)
    assert result is None

def test_require_jwt_or_api_key_with_jwt_direct(mocker):
    """Test require_jwt_or_api_key decorator logic with JWT token directly"""
    from flask import Flask, request as flask_request
    from security.jwt_auth import require_jwt_or_api_key
    
    test_app = Flask(__name__)
    test_app.config['TESTING'] = True
    
    @test_app.route('/test_jwt')
    @require_jwt_or_api_key
    def test_endpoint():
        return {'status': 'ok', 'user_id': flask_request.user_id}
    
    token = generate_jwt_token('user123', 'free')
    
    with test_app.test_client() as client:
        response = client.get('/test_jwt', headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['user_id'] == 'user123'

def test_require_jwt_or_api_key_with_api_key_direct(mocker):
    """Test require_jwt_or_api_key decorator logic with API key directly"""
    from flask import Flask
    from security.jwt_auth import require_jwt_or_api_key
    from middleware.auth import APIKeyManager, RateLimiter
    
    test_app = Flask(__name__)
    test_app.config['TESTING'] = True
    
    mock_key_data = {
        'user_id': 'user123',
        'tier': 'free',
        'is_active': 'true'
    }
    mocker.patch.object(APIKeyManager, 'get_key_data', return_value=mock_key_data)
    mocker.patch.object(RateLimiter, 'check_rate_limit', return_value=(True, {}))
    
    @test_app.route('/test_api_key')
    @require_jwt_or_api_key
    def test_endpoint():
        return {'status': 'ok'}
    
    with test_app.test_client() as client:
        response = client.get('/test_api_key', headers={'X-API-Key': 'valid_key'})
        assert response.status_code == 200

def test_require_jwt_or_api_key_invalid_jwt_direct():
    """Test require_jwt_or_api_key decorator with invalid JWT directly"""
    from flask import Flask
    from security.jwt_auth import require_jwt_or_api_key
    
    test_app = Flask(__name__)
    test_app.config['TESTING'] = True
    
    @test_app.route('/test_invalid_jwt')
    @require_jwt_or_api_key
    def test_endpoint():
        return {'status': 'ok'}
    
    with test_app.test_client() as client:
        response = client.get('/test_invalid_jwt', headers={'Authorization': 'Bearer invalid_token'})
        assert response.status_code == 401

def test_require_jwt_or_api_key_no_auth_direct():
    """Test require_jwt_or_api_key decorator without authentication directly"""
    from flask import Flask
    from security.jwt_auth import require_jwt_or_api_key
    
    test_app = Flask(__name__)
    test_app.config['TESTING'] = True
    
    @test_app.route('/test_no_auth')
    @require_jwt_or_api_key
    def test_endpoint():
        return {'status': 'ok'}
    
    with test_app.test_client() as client:
        response = client.get('/test_no_auth')
        assert response.status_code == 401

def test_require_jwt_or_api_key_expired_jwt_direct():
    """Test require_jwt_or_api_key decorator with expired JWT directly"""
    from flask import Flask
    from security.jwt_auth import require_jwt_or_api_key
    
    test_app = Flask(__name__)
    test_app.config['TESTING'] = True
    
    # Create expired token
    payload = {
        'user_id': 'user123',
        'tier': 'free',
        'iat': time.time() - 100000,
        'exp': time.time() - 50000,
        'type': 'access'
    }
    expired_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    @test_app.route('/test_expired_jwt')
    @require_jwt_or_api_key
    def test_endpoint():
        return {'status': 'ok'}
    
    with test_app.test_client() as client:
        response = client.get('/test_expired_jwt', headers={'Authorization': f'Bearer {expired_token}'})
        assert response.status_code == 401

def test_jwt_token_different_tiers():
    """Test JWT tokens for different tiers"""
    tiers = ['free', 'starter', 'professional', 'enterprise']
    
    for tier in tiers:
        token = generate_jwt_token('user123', tier)
        payload = validate_jwt_token(token)
        assert payload is not None
        assert payload['tier'] == tier
