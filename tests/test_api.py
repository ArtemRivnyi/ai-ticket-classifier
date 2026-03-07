import pytest
import os
import json
from app import app, db
from models import Feedback

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Use in-memory SQLite for tests to bypass PostgreSQL requirement locally
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_api_health(client):
    """Test health endpoint to ensure app loads"""
    rv = client.get('/api/v1/health')
    assert rv.status_code == 200
    assert 'healthy' in rv.get_json()['status']

def test_rate_limiting(client):
    """Test that rate limiting blocks excessive requests (assuming 3 per min on /api/contact)"""
    client.environ_base['REMOTE_ADDR'] = '127.0.0.99'
    
    # Send 3 requests
    for i in range(3):
        rv = client.post('/api/contact', json={'name': 'test', 'email': 'test@test.com', 'message': 'hello'})
        # Accept either 200 (if SMTP mocked well) or 503 (if SMTP failed), but not 429 yet
        assert rv.status_code in [200, 503, 500] 

    # 4th request should be blocked
    rv_blocked = client.post('/api/contact', json={'name': 'test', 'email': 'test@test.com', 'message': 'hello'})
    assert rv_blocked.status_code == 429
    assert 'Rate limit exceeded' in rv_blocked.get_json()['error']

def test_html_sanitization_bleach(client):
    """Test that bleach sanitizes malicious HTML tags from the ticket text"""
    malicious_ticket = "I need help with my router! <script>alert('xss');</script> <b>Please fix it</b>"
    
    # We test the classify endpoint. We expect 401 unauth without API key,
    # but the validation and sanitization happens BEFORE the provider error.
    # Actually, let's just test the Pydantic model itself to isolate the bleach logic.
    from app import TicketRequest
    
    request_data = {"ticket": malicious_ticket}
    model = TicketRequest(**request_data)
    
    sanitized = model.ticket
    assert "<script>" not in sanitized
    # Bleach strips tags by default in our app.py implementation, but leaves the text content
    assert "Please fix it" in sanitized

def test_feedback_saves_to_db(client):
    """Test that feedback properly saves to the SQLAlchemy database"""
    feedback_data = {
        "request_id": "test_req_123",
        "correct": True,
        "ticket": "My internet is down",
        "predicted": "Technical",
        "comments": "Good job"
    }
    
    rv = client.post('/api/v1/feedback', json=feedback_data)
    assert rv.status_code == 200
    
    # Verify in DB
    with app.app_context():
        feedbacks = Feedback.query.all()
        assert len(feedbacks) == 1
        assert feedbacks[0].request_id == "test_req_123"
        assert feedbacks[0].correct is True
