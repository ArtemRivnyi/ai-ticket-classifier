from __future__ import annotations

from flask import Blueprint, jsonify, request, current_app
from pydantic import BaseModel, Field, ValidationError

from middleware.auth import require_api_key
from integrations.zendesk_adapter import ZendeskAdapter


integrations_bp = Blueprint(
    "integrations",
    __name__,
    url_prefix="/api/v1/integrations",
)


class ZendeskTicketPayload(BaseModel):
    """Payload schema for Zendesk webhook requests."""

    ticket_id: int = Field(..., description="Zendesk ticket ID")
    subject: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1, max_length=10_000)
    requester_email: str | None = Field(default=None)
    priority: str | None = Field(default=None)
    via: str | None = Field(default=None)


@integrations_bp.route("/zendesk", methods=["POST"])
@require_api_key
def zendesk_webhook():
    """Zendesk webhook entrypoint -> classify ticket -> return update instructions."""
    classifier = current_app.config.get("CLASSIFIER")
    if not classifier:
        return (
            jsonify(
                {
                    "error": "Classification service unavailable",
                    "message": "No AI providers configured",
                }
            ),
            503,
        )

    try:
        if request.json is None:
            raise ValueError("JSON body required")
        payload = ZendeskTicketPayload(**request.json)
    except (ValidationError, ValueError) as exc:
        details = exc.errors() if hasattr(exc, "errors") else str(exc)
        return (
            jsonify(
                {
                    "error": "Validation error",
                    "details": details,
                }
            ),
            400,
        )

    ticket_text = ZendeskAdapter.compose_ticket_text(
        payload.subject, payload.description
    )
    try:
        classification = classifier.classify(ticket_text)
    except Exception as exc:  # pragma: no cover (propagated from providers)
        return (
            jsonify(
                {
                    "error": "Classification failed",
                    "message": str(exc),
                }
            ),
            502,
        )

    update_payload = ZendeskAdapter.build_update(payload.model_dump(), classification)

    return (
        jsonify(
            {
                "status": "processed",
                "ticket_id": payload.ticket_id,
                "zendesk": update_payload,
            }
        ),
        200,
    )
