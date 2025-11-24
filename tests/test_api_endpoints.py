import pytest
import json
from app import app
import os

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_feedback_endpoint(client):
    """Test submitting feedback"""
    # Create a dummy feedback request
    data = {
        "request_id": "test-req-123",
        "correct": True,
        "comments": "Great job!"
    }
    
    response = client.post('/api/v1/feedback', 
                          data=json.dumps(data),
                          content_type='application/json')
    
    print(f"DEBUG: Response: {response.json}")
    
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    
    # Verify file was created
    assert os.path.exists('feedback.json')
    
    # Clean up
    # os.remove('feedback.json') # Keep it for inspection if needed, or remove

def test_feedback_invalid_json(client):
    """Test submitting invalid JSON to feedback"""
    response = client.post('/api/v1/feedback', 
                          data="not json",
                          content_type='application/json')
    
    assert response.status_code == 400

def test_evaluation_results_endpoint(client):
    """Test fetching evaluation results"""
    # Ensure the file exists (it should from previous steps)
    if not os.path.exists('evaluation_results.json'):
        with open('evaluation_results.json', 'w') as f:
            json.dump({"accuracy": 90.0, "total": 10, "correct": 9, "results": []}, f)
            
    response = client.get('/api/v1/evaluation-results')
    assert response.status_code == 200
    data = response.json
    # Check for actual fields in evaluation results
    assert 'accuracy' in data or 'total' in data or 'results' in data

def test_about_page(client):
    """Test about page renders"""
    response = client.get('/about')
    assert response.status_code == 200
    assert b'AI Ticket Classifier' in response.data

def test_evaluation_page(client):
    """Test evaluation page renders"""
    response = client.get('/evaluation')
    assert response.status_code == 200
    assert b'Model Evaluation' in response.data
