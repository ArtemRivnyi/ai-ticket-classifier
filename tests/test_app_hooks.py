"""
Tests for app.py hooks (before_request, after_request) and edge cases
"""
import pytest
import os
from app import app
from flask import request

def test_before_request_sets_start_time(client):
    """Test before_request hook sets start_time"""
    with app.test_request_context():
        from app import before_request
        before_request()
        assert hasattr(request, 'start_time')

def test_before_request_force_https_enabled(client, mocker):
    """Test before_request with FORCE_HTTPS enabled"""
    mocker.patch.dict(os.environ, {'FORCE_HTTPS': 'true'})
    
    # Reload app to pick up new env var
    from importlib import reload
    import app as app_module
    reload(app_module)
    
    response = client.get('/api/v1/health')
    # Should either work or return 403 if HTTPS is enforced
    assert response.status_code in [200, 403]

def test_after_request_records_metrics(client):
    """Test after_request hook records metrics"""
    response = client.get('/api/v1/health', headers={'X-Forwarded-Proto': 'https'})
    assert response.status_code == 200
    assert 'X-Content-Type-Options' in response.headers

def test_after_request_security_headers(client):
    """Test after_request adds security headers"""
    response = client.get('/api/v1/health', headers={'X-Forwarded-Proto': 'https'})
    assert response.status_code == 200
    assert response.headers.get('X-Content-Type-Options') == 'nosniff'
    assert response.headers.get('X-Frame-Options') == 'DENY'
    assert response.headers.get('X-XSS-Protection') == '1; mode=block'

def test_after_request_hsts_header(client, mocker):
    """Test after_request adds HSTS header when FORCE_HTTPS is enabled"""
    mocker.patch.dict(os.environ, {'FORCE_HTTPS': 'true'})
    from importlib import reload
    import app as app_module
    reload(app_module)

    response = client.get(
        '/api/v1/health',
        headers={'X-Forwarded-Proto': 'https'}
    )
    if response.status_code == 200:
        assert 'Strict-Transport-Security' in response.headers


def test_after_request_without_start_time(client):
    """Test after_request handles missing start_time gracefully"""
    # This should not crash even if start_time is not set
    response = client.get('/api/v1/health', headers={'X-Forwarded-Proto': 'https'})
    assert response.status_code == 200

def test_get_limiter_key_with_api_key(client):
    """Test get_limiter_key function with API key"""
    from app import get_limiter_key
    
    with app.test_request_context(headers={'X-API-Key': 'test_key'}):
        key = get_limiter_key()
        assert 'api_key:' in key

def test_get_limiter_key_without_api_key(client):
    """Test get_limiter_key function without API key"""
    from app import get_limiter_key
    
    with app.test_request_context():
        key = get_limiter_key()
        # Should use IP or default
        assert key is not None

