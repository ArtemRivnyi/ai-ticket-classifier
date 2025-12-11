import pytest
from unittest.mock import MagicMock, patch
from app import app, cache

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['CACHE_TYPE'] = 'SimpleCache'
    with app.test_client() as client:
        yield client

def test_caching_behavior(client):
    """Test that subsequent requests with same ticket are cached"""
    
    # Mock the classifier to track calls
    with patch('app.classifier') as mock_classifier:
        # Setup mock return value
        mock_result = {
            'category': 'Test Category',
            'subcategory': 'Test Subcategory',
            'confidence': 0.99,
            'provider': 'mock_provider'
        }
        mock_classifier.classify.return_value = mock_result
        
        # Mock API key validation
        mock_key_data = {
            'id': 'test_key_id',
            'user_id': 'test_user',
            'tier': 'free',
            'is_active': 'true'
        }
        
        with patch('middleware.auth.APIKeyManager.get_key_data', return_value=mock_key_data):
             with patch('middleware.auth.RateLimiter.check_rate_limit', return_value=(True, {'reset_in': 0})):
                
                # Clear cache before test
                cache.clear()
                
                headers = {'X-API-Key': 'test-key', 'Content-Type': 'application/json'}
                payload = {'ticket': 'This is a test ticket for caching'}
                
                # First request - should call classifier
                response1 = client.post('/api/v1/classify', json=payload, headers=headers)
                assert response1.status_code == 200, f"Response: {response1.data}"
                assert response1.json['category'] == 'Test Category'
                assert mock_classifier.classify.call_count == 1
                
                # Second request - should NOT call classifier (cache hit)
                response2 = client.post('/api/v1/classify', json=payload, headers=headers)
                assert response2.status_code == 200
                assert response2.json['category'] == 'Test Category'
                assert mock_classifier.classify.call_count == 1  # Count should still be 1
                
                # Third request with DIFFERENT ticket - should call classifier
                payload_diff = {'ticket': 'Different ticket text'}
                response3 = client.post('/api/v1/classify', json=payload_diff, headers=headers)
                assert response3.status_code == 200
                assert mock_classifier.classify.call_count == 2
