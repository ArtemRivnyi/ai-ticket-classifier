import logging
from flask import Blueprint, request, jsonify
from database.models import SessionLocal, Webhook, User
from security.jwt_auth import require_jwt_or_api_key
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional

logger = logging.getLogger(__name__)

webhooks_bp = Blueprint("webhooks", __name__, url_prefix="/api/v1/webhooks")

class WebhookCreate(BaseModel):
    url: str = Field(..., description="Webhook URL")
    secret: Optional[str] = Field(None, description="Secret for signature verification")
    events: List[str] = Field(default=["classification.completed"], description="Events to subscribe to")

@webhooks_bp.route("", methods=["GET"])
@require_jwt_or_api_key
def list_webhooks():
    """List user webhooks"""
    user_id = request.user_id
    db = SessionLocal()
    try:
        webhooks = db.query(Webhook).filter(Webhook.user_id == int(user_id)).all()
        return jsonify({
            "webhooks": [
                {
                    "id": w.id,
                    "url": w.url,
                    "events": w.events.split(","),
                    "is_active": w.is_active,
                    "created_at": w.created_at.isoformat()
                } for w in webhooks
            ]
        })
    finally:
        db.close()

@webhooks_bp.route("", methods=["POST"])
@require_jwt_or_api_key
def create_webhook():
    """Register a new webhook"""
    user_id = request.user_id
    try:
        data = WebhookCreate(**request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    db = SessionLocal()
    try:
        # Check limit (e.g. 5 per user)
        count = db.query(Webhook).filter(Webhook.user_id == int(user_id)).count()
        if count >= 5:
            return jsonify({"error": "Webhook limit reached (max 5)"}), 400

        webhook = Webhook(
            user_id=int(user_id),
            url=str(data.url),
            secret=data.secret,
            events=",".join(data.events)
        )
        db.add(webhook)
        db.commit()
        
        return jsonify({
            "status": "success",
            "webhook_id": webhook.id,
            "message": "Webhook registered"
        }), 201
    except Exception as e:
        logger.error(f"Error creating webhook: {e}")
        return jsonify({"error": "Failed to create webhook"}), 500
    finally:
        db.close()

@webhooks_bp.route("/<int:webhook_id>", methods=["DELETE"])
@require_jwt_or_api_key
def delete_webhook(webhook_id):
    """Delete a webhook"""
    user_id = request.user_id
    db = SessionLocal()
    try:
        webhook = db.query(Webhook).filter(
            Webhook.id == webhook_id,
            Webhook.user_id == int(user_id)
        ).first()
        
        if not webhook:
            return jsonify({"error": "Webhook not found"}), 404
            
        db.delete(webhook)
        db.commit()
        return jsonify({"status": "success", "message": "Webhook deleted"})
    finally:
        db.close()
