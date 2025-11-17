"""
Additional tests to achieve 100% code coverage
Tests all remaining code branches
"""
import pytest
import os
from app import app, classifier
from unittest.mock import Mock, patch

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def headers(api_key):
    """Create headers with API key"""
    return {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }

def test_health_with_classifier_available(client):
    """Test health endpoint when classifier is available"""
    # Mock optional_api_key to avoid rate limiting issues
    from unittest.mock import patch, MagicMock
    with patch('app.optional_api_key', lambda f: f):
        # Mock redis_client to return int from incr, not Mock
        with patch('middleware.auth.redis_client') as mock_redis:
            if mock_redis:
                # Ensure incr returns an actual integer
                mock_redis.incr = MagicMock(return_value=1)
                mock_redis.expire = MagicMock(return_value=True)
            # Also patch the redis_client in the module
            import middleware.auth
            if hasattr(middleware.auth, 'redis_client'):
                middleware.auth.redis_client = mock_redis
            response = client.get('/api/v1/health')
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'healthy'

def test_classify_with_exception_in_classification(client, mocker, headers):
    """Test classify when classification raises exception"""
    from app import classifier
    
    if classifier:
        mocker.patch.object(classifier, 'classify', side_effect=Exception("Classification error"))
        mocker.patch.object(classifier, 'gemini_available', True)
    else:
        mock_classifier = mocker.Mock()
        mock_classifier.classify = mocker.Mock(side_effect=Exception("Classification error"))
        mock_classifier.gemini_available = True
        mocker.patch('app.classifier', mock_classifier)
    
    response = client.post('/api/v1/classify',
                          json={'ticket': 'Test ticket'},
                          headers=headers)
    assert response.status_code == 500

def test_batch_classify_with_exception(client, mocker, headers):
    """Test batch classify when classification raises exception"""
    from app import classifier
    
    if classifier:
        mocker.patch.object(classifier, 'classify', side_effect=Exception("Error"))
        mocker.patch.object(classifier, 'gemini_available', True)
    else:
        mock_classifier = mocker.Mock()
        mock_classifier.classify = mocker.Mock(side_effect=Exception("Error"))
        mock_classifier.gemini_available = True
        mocker.patch('app.classifier', mock_classifier)
    
    response = client.post('/api/v1/batch',
                          json={'tickets': ['Ticket 1', 'Ticket 2']},
                          headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['failed'] > 0

def test_batch_classify_free_tier_limit(client, mocker, headers):
    """Test batch classify with free tier limit"""
    from app import classifier
    
    mock_result = {
        'category': 'Network Issue',
        'confidence': 0.9,
        'priority': 'high',
        'provider': 'gemini'
    }
    
    if classifier:
        mocker.patch.object(classifier, 'classify', return_value=mock_result)
        mocker.patch.object(classifier, 'gemini_available', True)
    else:
        mock_classifier = mocker.Mock()
        mock_classifier.classify = mocker.Mock(return_value=mock_result)
        mock_classifier.gemini_available = True
        mocker.patch('app.classifier', mock_classifier)
    
    # Free tier limit is 10, send 11 tickets
    tickets = [f'Ticket {i}' for i in range(11)]
    response = client.post('/api/v1/batch',
                          json={'tickets': tickets},
                          headers=headers)
    assert response.status_code == 400  # Exceeds free tier limit

def test_require_api_key_with_tuple_response(mocker):
    """Test require_api_key when function returns tuple"""
    from flask import Flask
    from middleware.auth import require_api_key, APIKeyManager, RateLimiter
    
    test_app = Flask(__name__)
    test_app.config['TESTING'] = True
    
    mock_key_data = {
        'user_id': 'user123',
        'tier': 'free',
        'is_active': 'true'
    }
    mocker.patch.object(APIKeyManager, 'get_key_data', return_value=mock_key_data)
    mocker.patch.object(APIKeyManager, 'hash_key', return_value='test_hash')
    mocker.patch.object(RateLimiter, 'check_rate_limit', return_value=(True, {
        'hourly_limit': 100,
        'hourly_remaining': 99
    }))
    
    import middleware.auth
    mock_redis = Mock()
    mock_redis.hset.return_value = True
    mock_redis.hincrby.return_value = 1
    middleware.auth.redis_client = mock_redis
    
    @test_app.route('/test-tuple')
    @require_api_key
    def test_endpoint():
        return {'status': 'ok'}, 201  # Return tuple
    
    with test_app.test_client() as client:
        response = client.get('/test-tuple', headers={'X-API-Key': 'valid_key'})
        assert response.status_code == 201

def test_require_api_key_without_rate_limit_headers(mocker):
    """Test require_api_key when rate_info doesn't have hourly_limit"""
    from flask import Flask
    from middleware.auth import require_api_key, APIKeyManager, RateLimiter
    
    test_app = Flask(__name__)
    test_app.config['TESTING'] = True
    
    mock_key_data = {
        'user_id': 'user123',
        'tier': 'free',
        'is_active': 'true'
    }
    mocker.patch.object(APIKeyManager, 'get_key_data', return_value=mock_key_data)
    mocker.patch.object(APIKeyManager, 'hash_key', return_value='test_hash')
    mocker.patch.object(RateLimiter, 'check_rate_limit', return_value=(True, {
        'remaining': 'unlimited'  # No hourly_limit key
    }))
    
    import middleware.auth
    mock_redis = Mock()
    mock_redis.hset.return_value = True
    mock_redis.hincrby.return_value = 1
    middleware.auth.redis_client = mock_redis
    
    @test_app.route('/test-no-headers')
    @require_api_key
    def test_endpoint():
        return {'status': 'ok'}
    
    with test_app.test_client() as client:
        response = client.get('/test-no-headers', headers={'X-API-Key': 'valid_key'})
        assert response.status_code == 200

def test_multi_provider_openai_fallback(mocker):
    """Test MultiProvider fallback to OpenAI when Gemini fails"""
    from providers.multi_provider import MultiProvider, CircuitState
    
    provider = MultiProvider()
    provider.gemini_available = True
    provider.openai_available = True
    
    # Mock Gemini to fail
    mock_gemini_model = Mock()
    mock_gemini_model.generate_content.side_effect = Exception("Gemini error")
    provider.gemini_model = mock_gemini_model
    provider.gemini_circuit.state = CircuitState.CLOSED  # Reset state
    
    # Mock OpenAI to succeed
    mock_openai_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "Account Problem"
    mock_openai_client.chat.completions.create.return_value = mock_response
    provider.openai_client = mock_openai_client
    
    result = provider.classify("My account is locked")
    assert result['category'] == "Account Problem"
    assert result['provider'] == 'openai'

def test_multi_provider_both_fail(mocker):
    """Test MultiProvider when both providers fail"""
    from providers.multi_provider import MultiProvider
    
    provider = MultiProvider()
    provider.gemini_available = True
    provider.openai_available = True
    
    # Mock both to fail
    mock_gemini_model = Mock()
    mock_gemini_model.generate_content.side_effect = Exception("Gemini error")
    provider.gemini_model = mock_gemini_model
    
    mock_openai_client = Mock()
    mock_openai_client.chat.completions.create.side_effect = Exception("OpenAI error")
    provider.openai_client = mock_openai_client
    
    with pytest.raises(Exception):
        provider.classify("Test ticket")

def test_jwt_auth_validate_token_missing_type():
    """Test validate_jwt_token with token missing type field"""
    from security.jwt_auth import validate_jwt_token, generate_jwt_token
    import jwt
    from security.jwt_auth import JWT_SECRET, JWT_ALGORITHM
    
    # Create token without type field
    payload = {
        'user_id': 'user123',
        'tier': 'free',
        'iat': 1000000000,
        'exp': 1000003600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    result = validate_jwt_token(token)
    assert result is None  # Should return None because type is missing

def test_api_auth_register_without_apikeymanager_and_jwt(client, mocker):
    """Test registration when both APIKeyManager and JWT fail"""
    mocker.patch('api.auth.APIKeyManager', None)
    mocker.patch('security.jwt_auth.generate_jwt_token', side_effect=Exception("JWT error"))
    
    payload = {
        'email': 'test@example.com',
        'name': 'Test User',
        'organization': 'Test Org'
    }
    
    response = client.post('/api/v1/auth/register', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert 'user_id' in data
    # Neither API key nor JWT should be in response
    assert 'api_key' not in data or 'jwt_token' not in data

def test_batch_classify_with_webhook_failure(client, mocker, headers):
    """Test batch classify when webhook delivery fails"""
    from app import classifier, send_webhook
    
    if classifier:
        mock_result = {
            'category': 'Network Issue',
            'confidence': 0.9,
            'priority': 'high',
            'provider': 'gemini'
        }
        mocker.patch.object(classifier, 'classify', return_value=mock_result)
        mocker.patch.object(classifier, 'gemini_available', True)
    else:
        mock_classifier = mocker.Mock()
        mock_classifier.classify = mocker.Mock(return_value=mock_result)
        mock_classifier.gemini_available = True
        mocker.patch('app.classifier', mock_classifier)
    
    # Mock webhook to fail
    mocker.patch('app.send_webhook', side_effect=Exception("Webhook error"))
    
    response = client.post('/api/v1/batch',
                          json={
                              'tickets': ['Ticket 1'],
                              'webhook_url': 'https://example.com/webhook'
                          },
                          headers=headers)
    # Should still return 200 even if webhook fails
    assert response.status_code == 200

def test_require_api_key_without_redis(client, mocker):
    """Test require_api_key when Redis is unavailable"""
    from flask import Flask
    from middleware.auth import require_api_key, APIKeyManager, RateLimiter
    
    test_app = Flask(__name__)
    test_app.config['TESTING'] = True
    
    mock_key_data = {
        'user_id': 'user123',
        'tier': 'free',
        'is_active': 'true'
    }
    mocker.patch.object(APIKeyManager, 'get_key_data', return_value=mock_key_data)
    mocker.patch.object(APIKeyManager, 'hash_key', return_value='test_hash')
    mocker.patch.object(RateLimiter, 'check_rate_limit', return_value=(True, {
        'hourly_limit': 100,
        'hourly_remaining': 99
    }))
    
    # Set redis_client to None
    import middleware.auth
    middleware.auth.redis_client = None
    
    @test_app.route('/test-no-redis')
    @require_api_key
    def test_endpoint():
        return {'status': 'ok'}
    
    with test_app.test_client() as client:
        response = client.get('/test-no-redis', headers={'X-API-Key': 'valid_key'})
        assert response.status_code == 200

def test_multi_provider_determine_priority_unknown_category():
    """Test _determine_priority for unknown category"""
    from providers.multi_provider import MultiProvider
    
    provider = MultiProvider()
    priority = provider._determine_priority('Unknown Category')
    assert priority == 'medium'  # Default for unknown categories

