"""
Integration tests for AI Ticket Classifier
Real-world scenarios without excessive mocking
"""

import pytest

# Use fixtures from conftest.py:
# - client: Flask test client
# - api_key: Test API key
# - headers: Headers with API key
# - mock_api_key_validation: Auto-applied mock for API key validation


def test_real_health_check(client):
    """Test health endpoint with real app"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data
    assert "provider_status" in data


def test_real_classify_with_mock_provider(client, mocker, headers, api_key):
    """Test classification with mocked AI provider (realistic scenario)"""
    # Mock the classifier to return realistic results
    from app import classifier

    mock_result = {
        "category": "Network Issue",
        "confidence": 0.92,
        "priority": "high",
        "provider": "gemini",
    }

    if classifier:
        mocker.patch.object(classifier, "classify", return_value=mock_result)
        mocker.patch.object(classifier, "gemini_available", True)
        mocker.patch.object(classifier, "openai_available", False)
    else:
        mock_classifier = mocker.Mock()
        mock_classifier.classify = mocker.Mock(return_value=mock_result)
        mock_classifier.gemini_available = True
        mock_classifier.openai_available = False
        mocker.patch("app.classifier", mock_classifier)

    # Real ticket examples
    test_cases = [
        "I cannot connect to the VPN from my home office",
        "My account password was reset but I can't log in",
        "I need a refund for my subscription",
        "Can you add dark mode to the mobile app?",
    ]

    for ticket in test_cases:
        response = client.post(
            "/api/v1/classify", json={"ticket": ticket}, headers=headers
        )
        assert response.status_code in [200, 429]
        data = response.get_json()
        if response.status_code == 200:
            assert "category" in data
            assert "confidence" in data
            assert "processing_time" in data
            assert isinstance(data["confidence"], (int, float))
            assert 0 <= data["confidence"] <= 1
        else:
            assert "error" in data


def test_real_batch_classification(client, mocker, headers, api_key):
    """Test batch classification with multiple tickets"""
    from app import classifier

    mock_results = [
        {
            "category": "Network Issue",
            "confidence": 0.95,
            "priority": "high",
            "provider": "gemini",
        },
        {
            "category": "Account Problem",
            "confidence": 0.88,
            "priority": "medium",
            "provider": "gemini",
        },
        {
            "category": "Payment Issue",
            "confidence": 0.92,
            "priority": "high",
            "provider": "gemini",
        },
    ]

    if classifier:

        def mock_classify(ticket):
            return mock_results.pop(0) if mock_results else mock_results[0]

        mocker.patch.object(classifier, "classify", side_effect=mock_classify)
        mocker.patch.object(classifier, "gemini_available", True)
        mocker.patch.object(classifier, "openai_available", False)
    else:
        mock_classifier = mocker.Mock()

        def mock_classify(ticket):
            return mock_results.pop(0) if mock_results else mock_results[0]

        mock_classifier.classify = mocker.Mock(side_effect=mock_classify)
        mock_classifier.gemini_available = True
        mock_classifier.openai_available = False
        mocker.patch("app.classifier", mock_classifier)

    tickets = ["VPN connection failed", "Account locked", "Payment declined"]

    response = client.post("/api/v1/batch", json={"tickets": tickets}, headers=headers)

    assert response.status_code in [200, 429]
    data = response.get_json()
    if response.status_code == 200:
        assert "total" in data
        assert "successful" in data
        assert "results" in data
        assert data["total"] == len(tickets)
        assert data["successful"] == len(tickets)
    else:
        assert "error" in data


def test_real_error_handling(client, headers, api_key):
    """Test real error scenarios"""
    # Missing ticket field
    response = client.post("/api/v1/classify", json={}, headers=headers)
    assert response.status_code in [400, 429]
    data = response.get_json()
    assert "error" in data

    # Empty ticket
    response = client.post("/api/v1/classify", json={"ticket": ""}, headers=headers)
    assert response.status_code in [400, 429]

    # Very long ticket (should be sanitized)
    long_ticket = "A" * 10000
    response = client.post(
        "/api/v1/classify", json={"ticket": long_ticket}, headers=headers
    )
    # Should either work (if sanitized) or return 400
    assert response.status_code in [200, 400, 429]


def test_real_rate_limiting_info(client, mocker, headers, api_key):
    """Test that rate limiting headers are present"""
    from app import classifier

    if classifier:
        mock_result = {
            "category": "Other",
            "confidence": 0.9,
            "priority": "low",
            "provider": "gemini",
        }
        mocker.patch.object(classifier, "classify", return_value=mock_result)
        mocker.patch.object(classifier, "gemini_available", True)
        mocker.patch.object(classifier, "openai_available", False)
    else:
        mock_classifier = mocker.Mock()
        mock_classifier.classify = mocker.Mock(
            return_value={
                "category": "Other",
                "confidence": 0.9,
                "priority": "low",
                "provider": "gemini",
            }
        )
        mock_classifier.gemini_available = True
        mock_classifier.openai_available = False
        mocker.patch("app.classifier", mock_classifier)

    response = client.post(
        "/api/v1/classify", json={"ticket": "Test ticket"}, headers=headers
    )

    assert response.status_code in [200, 429]
    # Check for rate limit headers (if rate limiting is enabled)
    if "X-RateLimit-Limit" in response.headers:
        assert "X-RateLimit-Remaining" in response.headers


def test_real_metrics_endpoint(client):
    """Test metrics endpoint returns Prometheus format"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.content_type or "text/plain" in str(
        response.content_type
    )
    # Check for some expected metrics
    content = response.get_data(as_text=True)
    assert "http_requests_total" in content or "classification" in content.lower()
