import pytest
import os
import json
from app_factory import create_app
from extensions import db, limiter

@pytest.fixture
def app():
    # Force testing mode
    os.environ["FLASK_ENV"] = "development"
    os.environ["MASTER_API_KEY"] = "test_master_key_32_chars_long_exactly"
    os.environ["SECRET_KEY"] = "test_secret_key_32_chars_long_exactly"
    
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_health_endpoint(client):
    """Test the admin health endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"

def test_main_routes(client):
    """Test that frontend routes are reachable"""
    for route in ["/", "/about", "/dashboard", "/login"]:
        response = client.get(route)
        assert response.status_code == 200

def test_analytics_api(client):
    """Test the analytics data endpoint"""
    response = client.get("/api/analytics/stats")
    assert response.status_code == 200
    data = response.get_json()
    assert "accuracy_over_time" in data
    assert "category_distribution" in data

def test_classification_requires_api_key(client):
    """Test that classification endpoints are protected"""
    response = client.post("/api/v1/classify", json={"ticket": "test ticket"})
    # Should be 401 Unauthorized if no API key provided
    assert response.status_code == 401

def test_invalid_blueprint_route(client):
    """Test 404 handler in refactored app"""
    response = client.get("/non_existent_route")
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Not found"
