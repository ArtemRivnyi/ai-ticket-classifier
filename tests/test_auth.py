"""
Authentication Tests
Tests for API key authentication and rate limiting
"""

import pytest
import json
import time
from app import app
from auth.api_keys import api_key_manager


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['TEST_MODE'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def test_api_key():
    """Generate a test API key"""
    api_key = api_key_manager.generate_key(
        client_name="Test Client",
        tier="free"
    )
    yield api_key
    # Cleanup after test
    api_key_manager.deactivate_key(api_key)


@pytest.fixture
def pro_api_key():
    """Generate a professional tier API key"""
    api_key = api_key_manager.generate_key(
        client_name="Pro Client",
        tier="professional"
    )
    yield api_key
    api_key_manager.deactivate_key(api_key)


class TestAuthentication:
    """Test authentication functionality"""
    
    def test_missing_api_key(self, client):
        """Test request without API key is rejected"""
        response = client.post(
            '/api/v1/classify',
            data=json.dumps({'ticket': 'Test ticket'}),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert data['code'] == 'AUTH_001'
    
    def test_invalid_api_key(self, client):
        """Test request with invalid API key is rejected"""
        response = client.post(
            '/api/v1/classify',
            data=json.dumps({'ticket': 'Test ticket'}),
            content_type='application/json',
            headers={'X-API-Key': 'invalid_key_12345'}
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert data['code'] == 'AUTH_002'
    
    def test_valid_api_key(self, client, test_api_key):
        """Test request with valid API key succeeds"""
        response = client.post(
            '/api/v1/classify',
            data=json.dumps({'ticket': 'VPN connection problem'}),
            content_type='application/json',
            headers={'X-API-Key': test_api_key}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'category' in data
        assert 'confidence' in data
    
    def test_inactive_api_key(self, client, test_api_key):
        """Test request with inactive API key is rejected"""
        # Deactivate the key
        api_key_manager.deactivate_key(test_api_key)
        
        response = client.post(
            '/api/v1/classify',
            data=json.dumps({'ticket': 'Test ticket'}),
            content_type='application/json',
            headers={'X-API-Key': test_api_key}
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'inactive' in data['message'].lower()


class TestAPIKeyManager:
    """Test API key management"""
    
    def test_generate_api_key(self):
        """Test API key generation"""
        api_key = api_key_manager.generate_key(
            client_name="Test Client",
            tier="free"
        )
        
        assert api_key.startswith('tk_')
        assert len(api_key) > 40
        
        # Cleanup
        api_key_manager.deactivate_key(api_key)
    
    def test_validate_api_key(self, test_api_key):
        """Test API key validation"""
        is_valid, key_data, error = api_key_manager.validate_key(test_api_key)
        
        assert is_valid is True
        assert key_data is not None
        assert key_data['tier'] == 'free'
        assert error is None
    
    def test_invalid_tier(self):
        """Test generating key with invalid tier raises error"""
        with pytest.raises(ValueError):
            api_key_manager.generate_key(
                client_name="Test",
                tier="invalid_tier"
            )
    
    def test_usage_increment(self, test_api_key):
        """Test usage counter increment"""
        # Get initial usage
        is_valid, key_data_before, _ = api_key_manager.validate_key(test_api_key)
        usage_before = key_data_before['usage']['total_requests']
        
        # Increment usage
        api_key_manager.increment_usage(test_api_key)
        
        # Check usage increased
        is_valid, key_data_after, _ = api_key_manager.validate_key(test_api_key)
        usage_after = key_data_after['usage']['total_requests']
        
        assert usage_after == usage_before + 1
    
    def test_tier_limits(self):
        """Test tier limits are correctly set"""
        tiers = ['free', 'starter', 'professional', 'enterprise']
        
        for tier in tiers:
            api_key = api_key_manager.generate_key(
                client_name=f"Test {tier}",
                tier=tier
            )
            
            is_valid, key_data, _ = api_key_manager.validate_key(api_key)
            
            assert key_data['tier'] == tier
            assert 'limits' in key_data
            assert 'requests_per_minute' in key_data['limits']
            
            # Cleanup
            api_key_manager.deactivate_key(api_key)


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limit_exceeded(self, client, test_api_key):
        """Test rate limiting kicks in after limit is exceeded"""
        # Make multiple requests quickly
        responses = []
        
        for i in range(15):  # Exceed the free tier limit
            response = client.post(
                '/api/v1/classify',
                data=json.dumps({'ticket': f'Test ticket {i}'}),
                content_type='application/json',
                headers={'X-API-Key': test_api_key}
            )
            responses.append(response)
            time.sleep(0.1)  # Small delay
        
        # Check that at least one request was rate limited
        rate_limited = any(r.status_code == 429 for r in responses)
        assert rate_limited, "Expected at least one 429 response"
    
    def test_pro_tier_higher_limits(self, client, pro_api_key):
        """Test professional tier has higher rate limits"""
        # Professional tier should handle more requests
        responses = []
        
        for i in range(20):
            response = client.post(
                '/api/v1/classify',
                data=json.dumps({'ticket': f'Test ticket {i}'}),
                content_type='application/json',
                headers={'X-API-Key': pro_api_key}
            )
            responses.append(response)
            time.sleep(0.05)
        
        # Most requests should succeed for pro tier
        successful = sum(1 for r in responses if r.status_code == 200)
        assert successful > 15, f"Expected > 15 successful requests, got {successful}"


class TestAdminEndpoints:
    """Test admin endpoints"""
    
    def test_admin_generate_key_without_secret(self, client):
        """Test admin endpoint requires admin secret"""
        response = client.post(
            '/api/v1/admin/generate-key',
            data=json.dumps({
                'client_name': 'New Client',
                'tier': 'free'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
    
    def test_admin_generate_key_with_invalid_secret(self, client):
        """Test admin endpoint rejects invalid secret"""
        response = client.post(
            '/api/v1/admin/generate-key',
            data=json.dumps({
                'client_name': 'New Client',
                'tier': 'free'
            }),
            content_type='application/json',
            headers={'X-Admin-Secret': 'invalid_secret'}
        )
        
        assert response.status_code == 401
    
    def test_admin_list_keys(self, client):
        """Test admin can list API keys"""
        from config.settings import Config
        
        response = client.get(
            '/api/v1/admin/keys',
            headers={'X-Admin-Secret': Config.ADMIN_SECRET}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'keys' in data
        assert 'total' in data


class TestInputValidation:
    """Test input validation"""
    
    def test_empty_ticket(self, client, test_api_key):
        """Test empty ticket is rejected"""
        response = client.post(
            '/api/v1/classify',
            data=json.dumps({'ticket': ''}),
            content_type='application/json',
            headers={'X-API-Key': test_api_key}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'empty' in data['message'].lower()
    
    def test_missing_ticket_field(self, client, test_api_key):
        """Test missing ticket field is rejected"""
        response = client.post(
            '/api/v1/classify',
            data=json.dumps({'priority': 'high'}),
            content_type='application/json',
            headers={'X-API-Key': test_api_key}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'required' in data['message'].lower()
    
    def test_invalid_priority(self, client, test_api_key):
        """Test invalid priority value is rejected"""
        response = client.post(
            '/api/v1/classify',
            data=json.dumps({
                'ticket': 'Test ticket',
                'priority': 'invalid'
            }),
            content_type='application/json',
            headers={'X-API-Key': test_api_key}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'priority' in data['message'].lower()
    
    def test_invalid_json(self, client, test_api_key):
        """Test invalid JSON is rejected"""
        response = client.post(
            '/api/v1/classify',
            data='invalid json',
            content_type='application/json',
            headers={'X-API-Key': test_api_key}
        )
        
        assert response.status_code == 400


if __name__ == '__main__':
    pytest.main([__file__, '-v'])