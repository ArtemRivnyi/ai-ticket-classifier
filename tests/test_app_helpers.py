"""
Tests for app.py helper functions and edge cases
"""
import pytest
from app import sanitize_input, get_user_tier, get_rate_limit
from flask import Flask
from app import app
from unittest.mock import patch, Mock


def test_sanitize_input_null_bytes():
    """Test sanitize_input removes null bytes"""
    result = sanitize_input("test\x00string\x00")
    assert "\x00" not in result
    assert result == "teststring"  # Null bytes removed, not replaced with space


def test_sanitize_input_script_tags():
    """Test sanitize_input removes script tags"""
    result = sanitize_input("test<script>alert('xss')</script>test")
    assert "<script>" not in result
    # Bleach with strip=True keeps the content, which is safe as long as tags are removed
    assert result == "testalert('xss')test"


def test_sanitize_input_whitespace():
    """Test sanitize_input normalizes whitespace"""
    result = sanitize_input("test    string\n\n\n")
    assert result == "test string"


def test_sanitize_input_length_limit():
    """Test sanitize_input enforces length limit"""
    long_text = "a" * 10000
    result = sanitize_input(long_text)
    assert len(result) <= 5000


def test_sanitize_input_empty():
    """Test sanitize_input with empty/None input"""
    assert sanitize_input("") == ""
    assert sanitize_input(None) == ""


def test_get_user_tier_default():
    """Test get_user_tier returns default"""
    with app.test_request_context():
        tier = get_user_tier()
        assert tier == "free"


def test_get_user_tier_custom():
    """Test get_user_tier returns custom tier"""
    with app.test_request_context():
        from flask import request

        request.api_key_tier = "professional"
        tier = get_user_tier()
        assert tier == "professional"


def test_get_rate_limit_all_tiers():
    """Test get_rate_limit for all tiers"""
    with app.test_request_context():
        from flask import request

        tiers = {
            "free": "100 per hour; 10 per minute",
            "starter": "1000 per hour",
            "professional": "10000 per hour",
            "enterprise": "100000 per hour",
        }

        for tier, expected in tiers.items():
            request.api_key_tier = tier
            assert get_rate_limit() == expected


def test_get_rate_limit_unknown_tier():
    """Test get_rate_limit with unknown tier defaults to free"""
    with app.test_request_context():
        from flask import request

        request.api_key_tier = "unknown_tier"
        assert get_rate_limit() == "100 per hour; 10 per minute"
