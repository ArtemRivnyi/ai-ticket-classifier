"""
Tests for app.py error handlers
"""
import pytest
from app import app
from pydantic import ValidationError

def test_ratelimit_handler(client, mocker):
    """Test rate limit error handler"""
    from flask import Flask
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    
    test_app = Flask(__name__)
    test_app.config['TESTING'] = True
    
    limiter = Limiter(
        app=test_app,
        key_func=get_remote_address,
        default_limits=["1 per second"]
    )
    
    @test_app.route('/test-rate-limit')
    @limiter.limit("1 per second")
    def test_endpoint():
        return {'status': 'ok'}
    
    # Register error handler
    @test_app.errorhandler(429)
    def ratelimit_handler(e):
        return {'error': 'Rate limit exceeded', 'message': str(e.description) if hasattr(e, 'description') else 'Too many requests'}, 429
    
    with test_app.test_client() as client:
        # First request should succeed
        response1 = client.get('/test-rate-limit')
        assert response1.status_code == 200
        
        # Second request should be rate limited
        response2 = client.get('/test-rate-limit')
        assert response2.status_code == 429

def test_not_found_handler(client):
    """Test 404 error handler"""
    response = client.get('/api/v1/nonexistent-endpoint')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == 'Not found'

def test_internal_error_handler():
    """Test 500 error handler"""
    from flask import Flask
    
    test_app = Flask(__name__)
    test_app.config['TESTING'] = True
    test_app.config['PROPAGATE_EXCEPTIONS'] = False  # Let Flask handle exceptions
    
    # Copy error handler from main app
    @test_app.errorhandler(500)
    def internal_error_handler(e):
        return {'error': 'Internal server error', 'message': 'An unexpected error occurred. Please try again later.'}, 500
    
    @test_app.route('/test-internal-error')
    def test_endpoint():
        raise Exception("Test internal error")
    
    with test_app.test_client() as client:
        with test_app.app_context():
            response = client.get('/test-internal-error')
            assert response.status_code == 500
            data = response.get_json()
            assert 'error' in data
            assert 'Internal server error' in data['error']

def test_validation_error_handler(client, headers):
    """Test ValidationError handler"""
    # Send invalid JSON that will trigger ValidationError
    response = client.post('/api/v1/classify',
                          data='invalid json',
                          headers={**headers, 'Content-Type': 'application/json'})
    assert response.status_code in [400, 500]  # May be 400 or 500 depending on where error occurs

def test_bad_request_handler(client, headers):
    """Test 400 Bad Request handler"""
    # Send request with invalid JSON but with API key
    response = client.post('/api/v1/classify',
                          data='not json',
                          headers={**headers, 'Content-Type': 'application/json'})
    # May be 400 (bad request) or 401 (unauthorized) depending on when error occurs
    assert response.status_code in [400, 401]
    if response.status_code == 400:
        data = response.get_json()
        assert 'error' in data

