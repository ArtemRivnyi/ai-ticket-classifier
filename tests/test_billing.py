import pytest
from flask import Flask
from unittest.mock import Mock, patch
from api.billing import billing_bp
from database.models import User

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    app.register_blueprint(billing_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_db_session(mocker):
    mock_session = Mock()
    mocker.patch("api.billing.SessionLocal", return_value=mock_session)
    return mock_session

def test_create_checkout_session_success(client, mock_db_session, mocker):
    """Test successful checkout session creation"""
    # Mock user
    mock_user = Mock(spec=User)
    mock_user.id = 1
    mock_user.email = "test@example.com"
    mock_user.stripe_customer_id = "cus_test123"
    
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
    
    # Mock Stripe
    mock_stripe = mocker.patch("api.billing.stripe")
    mock_stripe.checkout.Session.create.return_value.url = "https://checkout.stripe.com/test"
    
    # Mock JWT auth (simulate logged in user)
    mocker.patch("security.jwt_auth.validate_jwt_token", return_value={"user_id": "1", "tier": "free", "type": "access"})
    
    # We need to bypass the @require_jwt_or_api_key decorator or mock it effectively.
    # Since we can't easily patch the decorator after import, we'll mock the request.user_id 
    # if the decorator sets it, OR we mock the token verification inside the decorator.
    # The decorator calls verify_jwt_token.
    
    headers = {"Authorization": "Bearer valid-token"}
    response = client.post("/api/v1/billing/create-checkout-session", 
                          json={"tier": "starter"},
                          headers=headers)
    
    assert response.status_code == 200
    assert response.get_json()["checkout_url"] == "https://checkout.stripe.com/test"

def test_create_checkout_session_invalid_tier(client, mocker):
    """Test checkout with invalid tier"""
    mocker.patch("security.jwt_auth.validate_jwt_token", return_value={"user_id": "1", "tier": "free", "type": "access"})
    
    headers = {"Authorization": "Bearer valid-token"}
    response = client.post("/api/v1/billing/create-checkout-session", 
                          json={"tier": "invalid"},
                          headers=headers)
    
    assert response.status_code == 400
    assert "Invalid tier" in response.get_json()["error"]

def test_webhook_checkout_completed(client, mock_db_session, mocker):
    """Test webhook handling for checkout completed"""
    # Mock Stripe Webhook construction
    mock_event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "metadata": {"user_id": "1", "tier": "pro"},
                "subscription": "sub_123"
            }
        }
    }
    mocker.patch("api.billing.stripe.Webhook.construct_event", return_value=mock_event)
    
    # Mock User
    mock_user = Mock(spec=User)
    mock_user.id = 1
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
    
    headers = {"Stripe-Signature": "valid_signature"}
    response = client.post("/api/v1/billing/webhook", data="payload", headers=headers)
    
    assert response.status_code == 200
    assert mock_user.tier == "pro"
    assert mock_user.subscription_id == "sub_123"
    assert mock_user.subscription_status == "active"
