"""
Tests for Pydantic models in app.py
"""

import pytest
from pydantic import ValidationError
from api.v1.classification import TicketRequest, BatchTicketRequest


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

    long_ticket = "A" * 15000
    # Should raise ValidationError because max_length is 10000
    with pytest.raises(ValidationError):
        TicketRequest(ticket=long_ticket)


def test_ticket_request_sanitize_null_bytes():
    """Test TicketRequest sanitization removes null bytes"""
    from api.v1.classification import sanitize_text

    assert "\x00" not in sanitize_text("test\x00string")


def test_ticket_request_sanitize_whitespace():
    """Test TicketRequest sanitization normalizes whitespace"""
    from api.v1.classification import sanitize_text

    assert sanitize_text("test   string\n\t") == "test string"


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
    from api.v1.classification import sanitize_text

    tickets = ["Ticket 1\x00", "  Ticket 2  ", ""]
    sanitized = [sanitize_text(t) for t in tickets if sanitize_text(t)]
    assert len(sanitized) >= 1
    assert "\x00" not in sanitized[0]
