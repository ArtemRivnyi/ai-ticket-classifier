import pytest
from flask import Flask
from unittest.mock import Mock, patch
from werkzeug.security import generate_password_hash
from api.auth import auth_bp
from database.models import User

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    app.register_blueprint(auth_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_db_session(mocker):
    mock_session = Mock()
    mocker.patch("api.auth.SessionLocal", return_value=mock_session)
    return mock_session

def test_login_success(client, mock_db_session, mocker):
    """Test successful login"""
    # Mock user
    mock_user = Mock(spec=User)
    mock_user.id = 1
    mock_user.email = "test@example.com"
    mock_user.password_hash = generate_password_hash("password123")
    mock_user.tier = "free"
    
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
    
    # Mock JWT generation
    mocker.patch("security.jwt_auth.generate_jwt_token", return_value="fake-jwt-token")
    
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["jwt_token"] == "fake-jwt-token"
    assert data["user"]["email"] == "test@example.com"

def test_login_invalid_credentials(client, mock_db_session):
    """Test login with wrong password"""
    mock_user = Mock(spec=User)
    mock_user.email = "test@example.com"
    mock_user.password_hash = generate_password_hash("password123")
    
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
    
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    assert "Invalid email or password" in response.get_json()["error"]

def test_login_user_not_found(client, mock_db_session):
    """Test login with non-existent user"""
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    response = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 401
    assert "Invalid email or password" in response.get_json()["error"]

def test_login_validation_error(client):
    """Test login with missing fields"""
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com"
        # Missing password
    })
    
    assert response.status_code == 400
    assert "Validation error" in response.get_json()["error"]
