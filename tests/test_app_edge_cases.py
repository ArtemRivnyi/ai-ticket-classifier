"""
Tests for edge cases and additional coverage
"""
import pytest
import os
from app import app, classifier
from unittest.mock import Mock, patch

def test_classify_with_rate_limit_exceeded(client, headers, mocker):
    """Test classification when rate limit is exceeded"""
    from middleware.auth import RateLimiter
    
    mocker.patch.object(RateLimiter, 'check_rate_limit', return_value=(False, {
        'limit': 100,
        'remaining': 0,
        'reset_in': 3600
    }))
    
    response = client.post('/api/v1/classify',
                          json={'ticket': 'Test ticket'},
                          headers=headers)
    assert response.status_code == 429

def test_batch_with_partial_failures(client, mocker, headers):
    """Test batch classification with partial failures"""
    from app import classifier
    
    if classifier:
        def mock_classify(ticket):
            if 'fail' in ticket.lower():
                raise Exception("Classification failed")
            return {
                'category': 'Network Issue',
                'confidence': 0.9,
                'priority': 'high',
                'provider': 'gemini'
            }
        
        mocker.patch.object(classifier, 'classify', side_effect=mock_classify)
        mocker.patch.object(classifier, 'gemini_available', True)
    else:
        mock_classifier = mocker.Mock()
        def mock_classify(ticket):
            if 'fail' in ticket.lower():
                raise Exception("Classification failed")
            return {
                'category': 'Network Issue',
                'confidence': 0.9,
                'priority': 'high',
                'provider': 'gemini'
            }
        mock_classifier.classify = mocker.Mock(side_effect=mock_classify)
        mock_classifier.gemini_available = True
        mocker.patch('app.classifier', mock_classifier)
    
    response = client.post('/api/v1/batch',
                          json={'tickets': ['Ticket 1', 'fail ticket', 'Ticket 3']},
                          headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['failed'] > 0

def test_classify_with_master_api_key(client, mocker):
    """Test classification with master API key"""
    master_key = os.getenv('MASTER_API_KEY', 'test_master_key')
    
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
        mock_classifier.classify = mocker.Mock(return_value={
            'category': 'Network Issue',
            'confidence': 0.9,
            'priority': 'high',
            'provider': 'gemini'
        })
        mock_classifier.gemini_available = True
        mocker.patch('app.classifier', mock_classifier)
    
    headers = {'X-API-Key': master_key, 'Content-Type': 'application/json'}
    response = client.post('/api/v1/classify',
                          json={'ticket': 'Test ticket'},
                          headers=headers)
    assert response.status_code == 200

def test_health_with_classifier_unavailable(client, mocker):
    """Test health endpoint when classifier is unavailable"""
    mocker.patch('app.classifier', None)
    
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'

def test_classify_with_special_characters(client, mocker, headers):
    """Test classification with special characters in ticket"""
    if classifier:
        mock_result = {
            'category': 'Other',
            'confidence': 0.8,
            'priority': 'medium',
            'provider': 'gemini'
        }
        mocker.patch.object(classifier, 'classify', return_value=mock_result)
        mocker.patch.object(classifier, 'gemini_available', True)
    else:
        mock_classifier = mocker.Mock()
        mock_classifier.classify = mocker.Mock(return_value=mock_result)
        mock_classifier.gemini_available = True
        mocker.patch('app.classifier', mock_classifier)
    
    special_ticket = "Ticket with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
    response = client.post('/api/v1/classify',
                          json={'ticket': special_ticket},
                          headers=headers)
    assert response.status_code == 200

def test_batch_with_single_ticket(client, mocker, headers):
    """Test batch classification with single ticket"""
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
    
    response = client.post('/api/v1/batch',
                          json={'tickets': ['Single ticket']},
                          headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['total'] == 1
    assert data['successful'] == 1

def test_webhook_with_custom_events(client, headers):
    """Test webhook creation with custom events"""
    payload = {
        'url': 'https://example.com/webhook',
        'secret': 'webhook_secret',
        'events': ['classification.completed', 'batch.completed']
    }
    
    response = client.post('/api/v1/webhooks', json=payload, headers=headers)
    assert response.status_code == 201
    data = response.get_json()
    assert len(data['events']) == 2

