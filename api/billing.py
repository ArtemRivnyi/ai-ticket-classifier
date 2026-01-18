import os
import stripe
import logging
from flask import Blueprint, request, jsonify, redirect
from database.models import SessionLocal, User
from security.jwt_auth import require_jwt_or_api_key

logger = logging.getLogger(__name__)

billing_bp = Blueprint("billing", __name__, url_prefix="/api/v1/billing")

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Map tiers to Stripe Price IDs
# You should replace these with your actual Price IDs from Stripe Dashboard
PRICE_IDS = {
    "starter": os.getenv("STRIPE_PRICE_STARTER", "price_starter_monthly"),
    "pro": os.getenv("STRIPE_PRICE_PRO", "price_pro_monthly"),
}

@billing_bp.route("/create-checkout-session", methods=["POST"])
@require_jwt_or_api_key
def create_checkout_session():
    """Create a Stripe Checkout Session for subscription"""
    try:
        data = request.json
        tier = data.get("tier")
        user_id = request.user_id # From JWT/API Key middleware
        
        if tier not in PRICE_IDS:
            return jsonify({"error": "Invalid tier"}), 400
            
        if not user_id:
             return jsonify({"error": "User authentication required"}), 401

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == int(user_id)).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
                
            # Create or get Stripe Customer
            if not user.stripe_customer_id:
                customer = stripe.Customer.create(
                    email=user.email,
                    metadata={"user_id": str(user.id)}
                )
                user.stripe_customer_id = customer.id
                db.commit()
            
            customer_id = user.stripe_customer_id
            
            # Create Checkout Session
            checkout_session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": PRICE_IDS[tier],
                        "quantity": 1,
                    },
                ],
                mode="subscription",
                success_url=request.host_url.rstrip("/") + "/dashboard?success=true",
                cancel_url=request.host_url.rstrip("/") + "/dashboard?canceled=true",
                metadata={"user_id": str(user.id), "tier": tier},
            )
            
            return jsonify({"checkout_url": checkout_session.url})
            
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        return jsonify({"error": str(e)}), 500

@billing_bp.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({"error": "Invalid signature"}), 400

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        handle_checkout_completed(session)
    elif event["type"] == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        # handle_payment_succeeded(invoice) # Optional: extend subscription
    
    return jsonify({"status": "success"})

def handle_checkout_completed(session):
    """Update user tier after successful checkout"""
    user_id = session.get("metadata", {}).get("user_id")
    tier = session.get("metadata", {}).get("tier")
    subscription_id = session.get("subscription")
    
    if user_id and tier:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == int(user_id)).first()
            if user:
                user.tier = tier
                user.subscription_id = subscription_id
                user.subscription_status = "active"
                db.commit()
                logger.info(f"User {user_id} upgraded to {tier}")
        except Exception as e:
            logger.error(f"Error updating user tier: {e}")
        finally:
            db.close()
