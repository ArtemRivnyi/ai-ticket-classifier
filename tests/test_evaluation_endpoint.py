"""
Tests for evaluation and CSV batch endpoints
"""

import pytest
from io import BytesIO
from unittest.mock import MagicMock


def test_run_evaluation_no_auth(client):
    """Test evaluation endpoint allows anonymous access for public demo"""
    response = client.post("/api/evaluation/run")
    # Should work without auth (200) or require dataset (404)
    assert response.status_code in [200, 404]


def test_batch_csv_no_file(client, headers):
    """Test CSV batch without file"""
    response = client.post("/api/v1/classify/batch-csv", headers=headers)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_batch_csv_invalid_extension(client, headers):
    """Test CSV batch with non-CSV file"""
    response = client.post(
        "/api/v1/classify/batch-csv",
        data={"file": (BytesIO(b"test"), "test.txt")},
        headers=headers,
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_batch_csv_success(client, headers, mocker):
    """Test successful CSV batch classification"""
    # Mock classifier
    mock_classifier = MagicMock()
    mock_classifier.classify.return_value = {
        "category": "Network Issue",
        "priority": "high",
        "provider": "gemini",
        "confidence": 0.95,
    }
    mocker.patch("app.classifier", mock_classifier)

    # Create CSV file
    csv_content = b"ticket\nVPN is down\nCannot login"

    response = client.post(
        "/api/v1/classify/batch-csv",
        data={"file": (BytesIO(csv_content), "test.csv")},
        headers=headers,
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "total" in data
    assert "successful" in data
    assert "results" in data
    assert data["total"] == 2


def test_batch_csv_empty_file(client, headers):
    """Test CSV batch with empty file"""
    csv_content = b""

    response = client.post(
        "/api/v1/classify/batch-csv",
        data={"file": (BytesIO(csv_content), "test.csv")},
        headers=headers,
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_batch_csv_classification_failure(client, headers, mocker):
    """Test CSV batch when classification fails"""
    # Mock classifier that raises exception
    mock_classifier = MagicMock()
    mock_classifier.classify.side_effect = Exception("Classification failed")
    mocker.patch("app.classifier", mock_classifier)

    csv_content = b"ticket\nVPN is down"

    response = client.post(
        "/api/v1/classify/batch-csv",
        data={"file": (BytesIO(csv_content), "test.csv")},
        headers=headers,
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "total" in data
    assert "failed" in data
    assert data["failed"] == 1


def test_index_page(client):
    """Test index page renders"""
    response = client.get("/")
    assert response.status_code == 200


def test_about_page_content(client):
    """Test about page has content"""
    response = client.get("/about")
    assert response.status_code == 200
    assert b"AI Ticket Classifier" in response.data or b"About" in response.data


def test_evaluation_page_content(client):
    """Test evaluation page has content"""
    response = client.get("/evaluation")
    assert response.status_code == 200
    assert b"Evaluation" in response.data or b"Model" in response.data
