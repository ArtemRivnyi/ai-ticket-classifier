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
