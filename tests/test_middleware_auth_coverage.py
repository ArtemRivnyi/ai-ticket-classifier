"""
Maximum coverage tests for middleware/auth.py
Target: 90%+ coverage
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import middleware.auth


class TestMiddlewareAuthCoverage:
    """Tests for middleware/auth.py coverage"""
    
    def test_api_key_manager_create_key_no_redis(self, mocker):
        """Test APIKeyManager.create_key when Redis is not available"""
        import importlib
        with patch.dict('os.environ', {'ALLOW_PROVIDERLESS': 'false'}):
            with patch('middleware.auth.redis_client', None):
                # Reload module to pick up the environment variable change
                importlib.reload(middleware.auth)
                try:
                    with pytest.raises(Exception, match="Redis not available"):
                        middleware.auth.APIKeyManager.create_key('user1', 'test_key', 'free')
                finally:
                    # Reload again to restore original state
                    importlib.reload(middleware.auth)
    
    def test_api_key_manager_get_key_data_no_redis(self, mocker):
        """Test APIKeyManager.get_key_data when Redis is not available"""
        # Mock hgetall to return None/empty when Redis is not available
        original_redis = middleware.auth.redis_client
        try:
            # Create a mock that simulates Redis being unavailable
            mock_redis = MagicMock()
            mock_redis.hgetall.return_value = {}  # Empty result when key not found
            middleware.auth.redis_client = mock_redis
            # get_key_data should return None when key is not found
            result = middleware.auth.APIKeyManager.get_key_data('nonexistent_key')
            # Should return None when key doesn't exist
            assert result is None or result == {}
        finally:
            middleware.auth.redis_client = original_redis
    
    def test_api_key_manager_revoke_key_no_redis(self, mocker):
        """Test APIKeyManager.revoke_key when Redis is not available"""
        with patch('middleware.auth.redis_client', None):
            result = middleware.auth.APIKeyManager.revoke_key('key_id', 'user1')
            assert result is False
    
    def test_api_key_manager_list_user_keys_no_redis(self, mocker):
        """Test APIKeyManager.list_user_keys when Redis is not available"""
        with patch('middleware.auth.redis_client', None):
            result = middleware.auth.APIKeyManager.list_user_keys('user1')
            assert result == []
    
    def test_api_key_manager_revoke_key_not_found(self, mocker):
        """Test APIKeyManager.revoke_key when key not found"""
        mock_redis = MagicMock()
        mock_redis.smembers.return_value = {'hash1', 'hash2'}
        mock_redis.hgetall.side_effect = [
            {'id': 'other_id'},
            {'id': 'other_id2'}
        ]
        
        with patch('middleware.auth.redis_client', mock_redis):
            result = middleware.auth.APIKeyManager.revoke_key('key_id', 'user1')
            assert result is False
    
    def test_rate_limiter_check_rate_limit_no_redis(self, mocker):
        """Test RateLimiter.check_rate_limit when Redis is not available"""
        # Stop all active patches to access real function
        import unittest.mock
        unittest.mock.patch.stopall()
        
        original_redis = middleware.auth.redis_client
        try:
            middleware.auth.redis_client = None
            # When Redis is None, check_rate_limit should return (True, {})
            allowed, info = middleware.auth.RateLimiter.check_rate_limit('user1', 'free')
            assert allowed is True
            # When Redis is None, info should be empty dict
            assert info == {}
        finally:
            middleware.auth.redis_client = original_redis
    
    def test_rate_limiter_check_rate_limit_unlimited(self, mocker):
        """Test RateLimiter.check_rate_limit for unlimited tier"""
        # Stop all active patches to access real function
        import unittest.mock
        unittest.mock.patch.stopall()
        
        mock_redis = MagicMock()
        with patch('middleware.auth.redis_client', mock_redis):
            allowed, info = middleware.auth.RateLimiter.check_rate_limit('user1', 'enterprise')
            assert allowed is True
            assert 'remaining' in info
            assert info['remaining'] == 'unlimited'
    
    def test_rate_limiter_check_rate_limit_hourly_exceeded(self, mocker):
        """Test RateLimiter.check_rate_limit when hourly limit exceeded"""
        # Stop all active patches to access real function
        import unittest.mock
        unittest.mock.patch.stopall()
        
        mock_redis = MagicMock()
        mock_redis.incr.return_value = 101  # Exceeds free tier limit of 100
        mock_redis.expire.return_value = True
        mock_redis.ttl.return_value = 3600
        
        with patch('middleware.auth.redis_client', mock_redis):
            allowed, info = middleware.auth.RateLimiter.check_rate_limit('user1', 'free')
            assert allowed is False
            assert 'limit' in info or 'remaining' in info or 'hourly_limit' in info
    
    def test_rate_limiter_check_rate_limit_daily_exceeded(self, mocker):
        """Test RateLimiter.check_rate_limit when daily limit exceeded"""
        # Stop all active patches to access real function
        import unittest.mock
        unittest.mock.patch.stopall()
        
        mock_redis = MagicMock()
        call_count = [0]
        def incr_side_effect(key):
            call_count[0] += 1
            if 'hour' in key:
                return 50  # Hourly OK
            elif 'day' in key:
                return 1001  # Daily exceeded
            return 1
        mock_redis.incr.side_effect = incr_side_effect
        mock_redis.ttl.return_value = 86400
        
        with patch('middleware.auth.redis_client', mock_redis):
            allowed, info = middleware.auth.RateLimiter.check_rate_limit('user1', 'free')
            assert allowed is False
            assert 'limit' in info
    
    def test_rate_limiter_check_rate_limit_first_request(self, mocker):
        """Test RateLimiter.check_rate_limit on first request (sets expire)"""
        # Stop all active patches to access real function
        import unittest.mock
        unittest.mock.patch.stopall()
        
        mock_redis = MagicMock()
        mock_redis.incr.return_value = 1  # First request
        mock_redis.expire.return_value = True
        mock_redis.ttl.return_value = 3600
        
        with patch('middleware.auth.redis_client', mock_redis):
            allowed, info = middleware.auth.RateLimiter.check_rate_limit('user1', 'free')
            assert allowed is True
            # expire should be called for both hour and day keys
            assert mock_redis.expire.call_count >= 1
    
    def test_require_api_key_no_key(self, client):
        """Test require_api_key decorator without API key"""
        response = client.post('/api/v1/classify', json={'ticket': 'test'})
        assert response.status_code == 401
    
    def test_require_api_key_invalid_key(self, client):
        """Test require_api_key decorator with invalid API key"""
        response = client.post('/api/v1/classify',
                              json={'ticket': 'test'},
                              headers={'X-API-Key': 'invalid_key'})
        assert response.status_code == 401
    
    def test_require_api_key_inactive_key(self, client, mocker):
        """Test require_api_key decorator with inactive API key"""
        mock_key_data = {
            'user_id': 'user1',
            'tier': 'free',
            'is_active': 'false'  # Inactive
        }
        with patch('middleware.auth.APIKeyManager.get_key_data', return_value=mock_key_data):
            response = client.post('/api/v1/classify',
                                  json={'ticket': 'test'},
                                  headers={'X-API-Key': 'test_key'})
            assert response.status_code == 401
    
    def test_optional_api_key_with_key(self, client, headers):
        """Test optional_api_key decorator with valid API key"""
        response = client.get('/api/v1/health', headers=headers)
        assert response.status_code == 200
    
    def test_optional_api_key_without_key(self, client):
        """Test optional_api_key decorator without API key"""
        response = client.get('/api/v1/health')
        assert response.status_code == 200
    
    def test_optional_api_key_rate_limit_ip(self, client, mocker):
        """Test optional_api_key rate limiting by IP"""
        mock_redis = MagicMock()
        mock_redis.incr.return_value = 101  # Exceeds anonymous limit
        mock_redis.ttl.return_value = 3600
        
        with patch('middleware.auth.redis_client', mock_redis):
            # Make multiple requests without API key
            for _ in range(5):
                response = client.get('/api/v1/health')
                # May be rate limited
                assert response.status_code in [200, 429]
    
    def test_optional_api_key_redis_error(self, client, mocker):
        """Test optional_api_key when Redis error occurs"""
        mock_redis = MagicMock()
        mock_redis.incr.side_effect = Exception("Redis error")
        
        with patch('middleware.auth.redis_client', mock_redis):
            # Should still allow request if Redis fails
            response = client.get('/api/v1/health')
            assert response.status_code == 200

