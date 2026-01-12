"""
Comprehensive tests for api/auth.py
Tests all endpoints and edge cases
"""
import pytest
from flask import Flask
from app import app
from api.auth import auth_bp, UserRegistration, CreateAPIKey


@pytest.fixture
def client():
    """Create test client"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def headers(api_key):
    """Create headers with API key"""
    return {"X-API-Key": api_key, "Content-Type": "application/json"}


def test_register_success(client, mocker):
    """Test successful user registration"""
    # Mock APIKeyManager
    mock_key_data = {
        "key": "atc_test_key_12345",
        "key_id": "test_key_id",
        "tier": "free",
        "created_at": "2025-01-01T00:00:00Z",
    }
    mocker.patch("api.auth.APIKeyManager.create_key", return_value=mock_key_data)
    mocker.patch("security.jwt_auth.generate_jwt_token", return_value="test_jwt_token")

    payload = {
        "email": "test@example.com",
        "name": "Test User",
        "organization": "Test Org",
    }

    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert "user_id" in data
    assert "api_key" in data
    assert "jwt_token" in data
    assert data["email"] == "test@example.com"


def test_register_validation_error(client):
    """Test registration with invalid data"""
    payload = {"email": "invalid-email", "name": "T", "organization": "O"}

    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_register_missing_fields(client):
    """Test registration with missing required fields"""
    payload = {"email": "test@example.com"}

    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400


def test_list_keys(client, headers, mocker):
    """Test listing API keys"""
    mock_keys = [
        {
            "id": "key1",
            "name": "Key 1",
            "tier": "free",
            "is_active": True,
            "created_at": "2025-01-01T00:00:00Z",
            "last_used": "",
            "requests_count": 10,
        }
    ]
    mocker.patch("api.auth.APIKeyManager.list_user_keys", return_value=mock_keys)

    response = client.get("/api/v1/auth/keys", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "keys" in data
    assert "total" in data


def test_create_key(client, headers, mocker):
    """Test creating a new API key"""
    mock_key_data = {
        "key": "atc_new_key_12345",
        "key_id": "new_key_id",
        "tier": "free",
        "created_at": "2025-01-01T00:00:00Z",
    }
    mocker.patch("api.auth.APIKeyManager.create_key", return_value=mock_key_data)

    payload = {"name": "New Key"}
    response = client.post("/api/v1/auth/keys", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.get_json()
    assert "key" in data
    assert "key_id" in data


def test_create_key_validation_error(client, headers):
    """Test creating key with invalid name"""
    payload = {"name": ""}  # Empty name

    response = client.post("/api/v1/auth/keys", json=payload, headers=headers)
    assert response.status_code == 400


def test_revoke_key(client, headers, mocker):
    """Test revoking an API key"""
    mocker.patch("api.auth.APIKeyManager.revoke_key", return_value=True)

    response = client.delete("/api/v1/auth/keys/test_key_id", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data


def test_revoke_key_not_found(client, headers, mocker):
    """Test revoking non-existent key"""
    mocker.patch("api.auth.APIKeyManager.revoke_key", return_value=False)

    response = client.delete("/api/v1/auth/keys/invalid_id", headers=headers)
    assert response.status_code == 404


def test_usage(client, headers):
    """Test getting usage statistics"""
    response = client.get("/api/v1/auth/usage", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "tier" in data
    assert "rate_limits" in data


def test_jwt_login_success(client, mocker):
    """Test JWT login with valid API key"""
    mock_key_data = {"user_id": "test_user", "tier": "free", "is_active": "true"}
    mocker.patch("api.auth.APIKeyManager.get_key_data", return_value=mock_key_data)
    mocker.patch("security.jwt_auth.generate_jwt_token", return_value="test_jwt_token")

    headers = {"X-API-Key": "test_api_key"}
    response = client.post("/api/v1/auth/jwt/login", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "jwt_token" in data
    assert "expires_in" in data


def test_jwt_login_invalid_key(client, mocker):
    """Test JWT login with invalid API key"""
    mocker.patch("api.auth.APIKeyManager.get_key_data", return_value=None)

    headers = {"X-API-Key": "invalid_key"}
    response = client.post("/api/v1/auth/jwt/login", headers=headers)
    assert response.status_code == 401


def test_jwt_login_no_key(client):
    """Test JWT login without API key"""
    response = client.post("/api/v1/auth/jwt/login")
    assert response.status_code == 401


def test_jwt_login_inactive_key(client, mocker):
    """Test JWT login with inactive API key"""
    mock_key_data = {"user_id": "test_user", "tier": "free", "is_active": "false"}
    mocker.patch("api.auth.APIKeyManager.get_key_data", return_value=mock_key_data)

    headers = {"X-API-Key": "inactive_key"}
    response = client.post("/api/v1/auth/jwt/login", headers=headers)
    assert response.status_code == 401
