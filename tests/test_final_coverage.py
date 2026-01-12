"""
Final coverage boost tests
"""

import pytest


def test_health_endpoint_basic(client):
    """Test basic health endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.get_json()
    assert "status" in data


def test_status_endpoint_basic(client, headers, mocker):
    """Test basic status endpoint"""
    # Mock classifier to return available status
    mock_classifier = mocker.patch("app.classifier")
    mock_classifier.get_status.return_value = {
        "gemini": "available",
        "openai": "unavailable",
    }
    mock_classifier.gemini_available = True
    mock_classifier.openai_available = False

    response = client.get("/api/v1/status", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "providers" in data


def test_status_endpoint_unavailable(client, headers, mocker):
    """Test status endpoint when providers are unavailable"""
    # Mock classifier to return unavailable status
    mock_classifier = mocker.patch("app.classifier")
    mock_classifier.get_status.return_value = {
        "gemini": "unavailable",
        "openai": "unavailable",
    }
    mock_classifier.gemini_available = False
    mock_classifier.openai_available = False

    # Ensure ALLOW_PROVIDERLESS is false
    mocker.patch("app.ALLOW_PROVIDERLESS", False)

    response = client.get("/api/v1/status", headers=headers)
    assert response.status_code == 503
    data = response.get_json()
    assert "error" in data
