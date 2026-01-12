"""
Tests for rate limiter module
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from security.rate_limiter import get_api_key, TIER_LIMITS, tier_rate_limit


def test_get_api_key_with_header():
    """Test get_api_key with X-API-Key header"""
    from flask import Flask, request

    app = Flask(__name__)
    with app.test_request_context(headers={"X-API-Key": "test_key_123"}):
        key = get_api_key()
        assert key == "test_key_123"


def test_get_api_key_without_header():
    """Test get_api_key without X-API-Key header (uses IP)"""
    from flask import Flask, request

    app = Flask(__name__)
    with app.test_request_context():
        with patch(
            "security.rate_limiter.get_remote_address", return_value="127.0.0.1"
        ):
            key = get_api_key()
            assert key == "127.0.0.1"


def test_tier_rate_limit_free():
    """Test tier_rate_limit for free tier"""
    from flask import Flask, request

    app = Flask(__name__)
    with app.test_request_context():
        request.user_tier = "free"
        limit = tier_rate_limit()
        assert limit == TIER_LIMITS["free"]


def test_tier_rate_limit_starter():
    """Test tier_rate_limit for starter tier"""
    from flask import Flask, request

    app = Flask(__name__)
    with app.test_request_context():
        request.user_tier = "starter"
        limit = tier_rate_limit()
        assert limit == TIER_LIMITS["starter"]


def test_tier_rate_limit_pro():
    """Test tier_rate_limit for pro tier"""
    from flask import Flask, request

    app = Flask(__name__)
    with app.test_request_context():
        request.user_tier = "pro"
        limit = tier_rate_limit()
        assert limit == TIER_LIMITS["pro"]


def test_tier_rate_limit_enterprise():
    """Test tier_rate_limit for enterprise tier"""
    from flask import Flask, request

    app = Flask(__name__)
    with app.test_request_context():
        request.user_tier = "enterprise"
        limit = tier_rate_limit()
        assert limit == TIER_LIMITS["enterprise"]


def test_tier_rate_limit_unknown():
    """Test tier_rate_limit for unknown tier (defaults to free)"""
    from flask import Flask, request

    app = Flask(__name__)
    with app.test_request_context():
        request.user_tier = "unknown_tier"
        limit = tier_rate_limit()
        assert limit == TIER_LIMITS["free"]


def test_tier_rate_limit_no_tier():
    """Test tier_rate_limit without tier (defaults to free)"""
    from flask import Flask, request

    app = Flask(__name__)
    with app.test_request_context():
        if hasattr(request, "user_tier"):
            delattr(request, "user_tier")
        limit = tier_rate_limit()
        assert limit == TIER_LIMITS["free"]
