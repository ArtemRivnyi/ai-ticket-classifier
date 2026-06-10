import pytest
import os
import json
from extensions import db
from app import app
from models import Feedback


@pytest.fixture
def client():
    app.config["TESTING"] = True
    # Use in-memory SQLite for tests to bypass PostgreSQL requirement locally
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


def test_api_health(client):
    """Test health endpoint to ensure app loads"""
    rv = client.get("/api/v1/health")
    assert rv.status_code == 200
    assert "healthy" in rv.get_json()["status"]


def test_html_sanitization_bleach(client):
    """Test that bleach sanitizes malicious HTML tags from the ticket text"""
    malicious_ticket = "I need help with my router! <script>alert('xss');</script> <b>Please fix it</b>"

    # We test the classify endpoint. We expect 401 unauth without API key,
    # but the validation and sanitization happens BEFORE the provider error.
    from api.v1.classification import sanitize_text

    sanitized = sanitize_text(malicious_ticket)
    assert "<script>" not in sanitized
    # Bleach strips tags by default in our app.py implementation, but leaves the text content
    assert "Please fix it" in sanitized
