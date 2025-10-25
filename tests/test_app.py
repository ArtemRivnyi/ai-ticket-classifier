import sys
import os
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask
from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test that /api/v1/health returns 200"""
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}
    print("✅ Health check passed")

def test_classify_valid_input(client, mocker):
    """Test /api/v1/classify with valid input"""
    mocker.patch('app.classify_ticket', return_value='Account Problem')
    payload = {'ticket': 'My account is locked', 'priority': 'high'}
    response = client.post('/api/v1/classify', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert 'category' in data
    assert data['category'] == 'Account Problem'
    assert data['priority'] == 'high'
    print(f"✅ Classification test passed - Category: {data['category']}, Priority: {data['priority']}")

def test_classify_valid_input_no_priority(client, mocker):
    """Test /api/v1/classify with valid input, no priority"""
    mocker.patch('app.classify_ticket', return_value='Account Problem')
    payload = {'ticket': 'My account is locked'}
    response = client.post('/api/v1/classify', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert 'category' in data
    assert data['category'] == 'Account Problem'
    assert data['priority'] == 'medium'  # Default value
    print(f"✅ Classification test passed (no priority) - Category: {data['category']}, Priority: {data['priority']}")

def test_classify_missing_ticket(client):
    """Test /api/v1/classify with missing ticket field"""
    payload = {'priority': 'high'}
    response = client.post('/api/v1/classify', json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'details' in data
    assert 'ticket' in data['details']
    assert 'Field required' in data['details']
    print("✅ Classification test passed - Missing ticket field")

def test_classify_invalid_ticket_type(client):
    """Test /api/v1/classify with invalid ticket type"""
    payload = {'ticket': 123, 'priority': 'low'}
    response = client.post('/api/v1/classify', json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'details' in data
    assert 'ticket' in data['details']
    assert 'Input should be a valid string' in data['details']
    print("✅ Classification test passed - Invalid ticket type")

def test_classify_invalid_json(client):
    """Test /api/v1/classify with invalid JSON"""
    response = client.post('/api/v1/classify', data="not_json")
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == 'Invalid JSON'
    print("✅ Classification test passed - Invalid JSON")