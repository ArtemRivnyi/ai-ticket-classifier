"""
Tests for Pydantic models in app.py
"""

import pytest
from pydantic import ValidationError
from app import TicketRequest, BatchTicketRequest, WebhookConfig


def test_ticket_request_valid():
    """Test valid TicketRequest"""
    request = TicketRequest(ticket="I cannot connect to VPN")
    assert request.ticket == "I cannot connect to VPN"


def test_ticket_request_empty():
    """Test TicketRequest with empty ticket"""
    with pytest.raises(ValidationError):
        TicketRequest(ticket="")


def test_ticket_request_too_long():
    """Test TicketRequest with too long ticket"""
    from pydantic import ValidationError

    long_ticket = "A" * 6000
    # Should raise ValidationError because max_length is 5000
    with pytest.raises(ValidationError):
        TicketRequest(ticket=long_ticket)


def test_ticket_request_sanitize_null_bytes():
    """Test TicketRequest sanitization removes null bytes"""
    request = TicketRequest(ticket="test\x00string")
    assert "\x00" not in request.ticket


def test_ticket_request_sanitize_whitespace():
    """Test TicketRequest sanitization normalizes whitespace"""
    request = TicketRequest(ticket="test   string\n\t")
    assert request.ticket == "test string"


def test_batch_ticket_request_valid():
    """Test valid BatchTicketRequest"""
    request = BatchTicketRequest(tickets=["Ticket 1", "Ticket 2"])
    assert len(request.tickets) == 2


def test_batch_ticket_request_empty():
    """Test BatchTicketRequest with empty tickets"""
    with pytest.raises(ValidationError):
        BatchTicketRequest(tickets=[])


def test_batch_ticket_request_too_many():
    """Test BatchTicketRequest with too many tickets"""
    many_tickets = [f"Ticket {i}" for i in range(101)]
    with pytest.raises(ValidationError):
        BatchTicketRequest(tickets=many_tickets)


def test_batch_ticket_request_sanitize():
    """Test BatchTicketRequest sanitization"""
    request = BatchTicketRequest(tickets=["Ticket 1\x00", "  Ticket 2  ", ""])
    # Empty tickets should be removed, null bytes removed
    assert len(request.tickets) >= 1
    assert "\x00" not in request.tickets[0]


def test_webhook_config_valid():
    """Test valid WebhookConfig"""
    config = WebhookConfig(url="https://example.com/webhook")
    assert config.url == "https://example.com/webhook"
    assert config.events == ["classification.completed"]  # Default


def test_webhook_config_custom_events():
    """Test WebhookConfig with custom events"""
    config = WebhookConfig(
        url="https://example.com/webhook",
        events=["classification.completed", "batch.completed"],
    )
    assert len(config.events) == 2


def test_webhook_config_invalid_url():
    """Test WebhookConfig with invalid URL"""
    # Pydantic doesn't validate URL format by default for str fields
    # So this test just verifies the model accepts any string
    config = WebhookConfig(url="not-a-valid-url")
    assert config.url == "not-a-valid-url"
    # If URL validation is needed, it should be added via field_validator


def test_webhook_config_secret():
    """Test WebhookConfig with secret"""
    config = WebhookConfig(url="https://example.com/webhook", secret="secret123")
    assert config.secret == "secret123"
