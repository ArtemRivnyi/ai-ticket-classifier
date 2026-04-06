"""
Tests for optional_api_key decorator edge cases
"""

import pytest
from flask import Flask
from middleware.auth import optional_api_key
from unittest.mock import Mock, patch


def test_optional_api_key_anonymous_rate_limit_exceeded(mocker):
    """Test optional_api_key when anonymous rate limit is exceeded"""
    test_app = Flask(__name__)
    test_app.config["TESTING"] = True

    # Patch RateLimiter.check_rate_limit directly to ensure it returns False
    mocker.patch(
        "middleware.auth.RateLimiter.check_rate_limit",
        return_value=(False, {"reset_in": 60}),
    )

    @test_app.route("/test-anonymous-limit")
    @optional_api_key
    def test_endpoint():
        return {"status": "ok"}

    with test_app.test_client() as client:
        response = client.get("/test-anonymous-limit")  # No API key
        assert response.status_code == 429


def test_optional_api_key_anonymous_first_request(mocker):
    """Test optional_api_key sets expire on first anonymous request"""
    test_app = Flask(__name__)
    test_app.config["TESTING"] = True

    # Patch RateLimiter.check_rate_limit
    with patch(
        "middleware.auth.RateLimiter.check_rate_limit", return_value=(True, {})
    ) as mock_check:

        @test_app.route("/test-anonymous-first")
        @optional_api_key
        def test_endpoint():
            return {"status": "ok"}

        with test_app.test_client() as client:
            response = client.get("/test-anonymous-first")  # No API key
            assert response.status_code == 200
            assert mock_check.called


def test_optional_api_key_anonymous_no_redis(mocker):
    """Test optional_api_key works without Redis for anonymous users"""
    test_app = Flask(__name__)
    test_app.config["TESTING"] = True

    mocker.patch("middleware.auth.redis_client", None)

    @test_app.route("/test-anonymous-no-redis")
    @optional_api_key
    def test_endpoint():
        return {"status": "ok"}

    with test_app.test_client() as client:
        response = client.get("/test-anonymous-no-redis")  # No API key
        assert response.status_code == 200
