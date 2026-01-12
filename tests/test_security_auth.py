"""
Tests for security/auth.py (legacy API key manager)
"""
import pytest
import os
from security.auth import APIKeyManager, api_key_manager, require_api_key


def test_api_key_manager_init():
    """Test APIKeyManager initialization"""
    manager = APIKeyManager()
    assert manager is not None
    assert hasattr(manager, "api_keys")


def test_generate_key():
    """Test API key generation"""
    manager = APIKeyManager()
    key, key_hash = manager.generate_key()

    assert key.startswith("sk_")
    assert len(key) > 40
    assert len(key_hash) == 64  # SHA256 hex length


def test_validate_key_valid():
    """Test validating a valid API key"""
    manager = APIKeyManager()
    master_key = os.getenv("MASTER_API_KEY", "dev_master_key_change_me")

    assert manager.validate_key(master_key) is True


def test_validate_key_invalid():
    """Test validating an invalid API key"""
    manager = APIKeyManager()
    assert manager.validate_key("invalid_key_123") is False


def test_get_tier():
    """Test getting user tier"""
    manager = APIKeyManager()
    master_key = os.getenv("MASTER_API_KEY", "dev_master_key_change_me")

    tier = manager.get_tier(master_key)
    assert tier == "enterprise"


def test_get_tier_default():
    """Test getting default tier for unknown key"""
    manager = APIKeyManager()
    tier = manager.get_tier("unknown_key")
    assert tier == "free"


def test_require_api_key_decorator_no_key():
    """Test require_api_key decorator without API key"""
    from flask import Flask
    from security.auth import require_api_key

    test_app = Flask(__name__)
    test_app.config["TESTING"] = True

    @test_app.route("/test-protected", methods=["GET"])
    @require_api_key
    def protected():
        return {"status": "ok"}

    with test_app.test_client() as client:
        response = client.get("/test-protected")
        assert response.status_code == 401


def test_require_api_key_decorator_invalid_key():
    """Test require_api_key decorator with invalid API key"""
    from flask import Flask
    from security.auth import require_api_key

    test_app = Flask(__name__)
    test_app.config["TESTING"] = True

    @test_app.route("/test-protected-invalid", methods=["GET"])
    @require_api_key
    def protected():
        return {"status": "ok"}

    with test_app.test_client() as client:
        response = client.get(
            "/test-protected-invalid", headers={"X-API-Key": "invalid_key"}
        )
        assert response.status_code == 403


def test_require_api_key_decorator_valid_key():
    """Test require_api_key decorator with valid API key"""
    from flask import Flask, request
    from security.auth import require_api_key

    test_app = Flask(__name__)
    test_app.config["TESTING"] = True

    @test_app.route("/test-protected-valid", methods=["GET"])
    @require_api_key
    def protected():
        return {"status": "ok", "tier": getattr(request, "user_tier", "unknown")}

    master_key = os.getenv("MASTER_API_KEY", "dev_master_key_change_me")
    with test_app.test_client() as client:
        response = client.get(
            "/test-protected-valid", headers={"X-API-Key": master_key}
        )
        assert response.status_code == 200
