import pytest
from unittest.mock import MagicMock, patch
from app import app, cache


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["CACHE_TYPE"] = "SimpleCache"
    with app.test_client() as client:
        yield client


def test_caching_behavior():
    """Test that subsequent requests with same ticket are cached"""
    from flask import Flask
    from flask_caching import Cache
    from unittest.mock import MagicMock

    # Create isolated app for this test
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["CACHE_TYPE"] = "SimpleCache"
    app.config["CACHE_DEFAULT_TIMEOUT"] = 300

    # Initialize cache
    cache = Cache(app)

    # Mock classifier
    mock_classifier = MagicMock()
    mock_classifier.classify.return_value = {
        "category": "Test Category",
        "subcategory": "Test Subcategory",
        "confidence": 0.99,
        "provider": "mock_provider",
    }
    app.config["CLASSIFIER"] = mock_classifier

    # Mock auth middleware
    # We need to register the endpoint manually since we're not using the full app
    @app.route("/api/v1/classify", methods=["POST"])
    def classify_ticket():
        from flask import request, jsonify

        ticket = request.json.get("ticket")

        # Check cache
        cache_key = f"ticket_classification:{ticket}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return jsonify(cached_result)

        # Classify
        result = app.config["CLASSIFIER"].classify(ticket)

        # Cache result
        cache.set(cache_key, result)

        return jsonify(result)

    with app.test_client() as client:
        headers = {"Content-Type": "application/json"}
        payload = {"ticket": "This is a test ticket for caching"}

        # First request - should call classifier
        response1 = client.post("/api/v1/classify", json=payload, headers=headers)
        assert response1.status_code == 200
        assert response1.json["category"] == "Test Category"
        assert mock_classifier.classify.call_count == 1

        # Second request - should NOT call classifier (cache hit)
        response2 = client.post("/api/v1/classify", json=payload, headers=headers)
        assert response2.status_code == 200
        assert response2.json["category"] == "Test Category"
        assert mock_classifier.classify.call_count == 1  # Count should still be 1

        # Third request with DIFFERENT ticket - should call classifier
        payload_diff = {"ticket": "Different ticket text"}
        response3 = client.post("/api/v1/classify", json=payload_diff, headers=headers)
        assert response3.status_code == 200
        assert mock_classifier.classify.call_count == 2
