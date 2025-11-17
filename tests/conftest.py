"""
Pytest configuration and shared fixtures
"""
import pytest
import os
import sys
from pathlib import Path
from unittest.mock import patch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

@pytest.fixture(scope="session")
def app():
    """Create Flask app for testing"""
    from app import app as flask_app
    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = 'test-secret-key'
    flask_app.config['JWT_SECRET'] = 'test-jwt-secret'
    
    # Disable rate limiting in tests
    flask_app.config['RATELIMIT_ENABLED'] = False
    
    return flask_app

@pytest.fixture
def client(app):
    """Create test client"""
    with app.test_client() as client:
        yield client

@pytest.fixture
def api_key():
    """Generate a test API key"""
    # Use master API key for testing
    return os.getenv('MASTER_API_KEY', 'test_api_key_for_testing')

@pytest.fixture(autouse=True)
def mock_api_key_validation(api_key):
    """Mock API key validation to always return valid for test keys"""
    from middleware.auth import APIKeyManager, RateLimiter
    
    # Mock get_key_data to return valid key data
    def mock_get_key_data(key):
        if key == api_key or key.startswith('test_') or key.startswith('atc_') or key == os.getenv('MASTER_API_KEY', ''):
            return {
                'id': 'test_key_id',
                'key_hash': 'test_hash',
                'user_id': 'test_user',
                'name': 'Test Key',
                'tier': 'free',
                'is_active': 'true',
                'created_at': '2025-01-01T00:00:00Z',
                'last_used': '',
                'requests_count': '0',
                'rate_limit': '100'
            }
        return None
    
    # Mock rate limiter to always allow
    def mock_check_rate_limit(user_id, tier):
        return True, {
            'hourly_limit': 100,
            'hourly_remaining': 99,
            'daily_limit': 1000,
            'daily_remaining': 999,
            'reset_in': 3600
        }
    
    # Patch at module level using unittest.mock - keep patches active for entire test
    patcher1 = patch('middleware.auth.APIKeyManager.get_key_data', side_effect=mock_get_key_data)
    patcher2 = patch('middleware.auth.RateLimiter.check_rate_limit', side_effect=mock_check_rate_limit)
    
    patcher1.start()
    patcher2.start()
    
    yield
    
    patcher1.stop()
    patcher2.stop()

@pytest.fixture
def headers(api_key):
    """Create headers with API key"""
    return {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }

@pytest.fixture
def mock_redis_client(mocker):
    """Mock Redis client for tests"""
    from unittest.mock import Mock
    mock_redis = Mock()
    mock_redis.ping.return_value = True
    mock_redis.hgetall.return_value = {}
    mock_redis.hset.return_value = True
    mock_redis.sadd.return_value = True
    mock_redis.smembers.return_value = set()
    # Use side_effect to return actual integers, not Mock objects
    mock_redis.incr.side_effect = lambda key: 1  # Default to 1
    mock_redis.expire.return_value = True
    mock_redis.get.return_value = None
    mock_redis.ttl.return_value = 3600
    mock_redis.hincrby.return_value = 1
    
    mocker.patch('middleware.auth.redis_client', mock_redis)
    return mock_redis

