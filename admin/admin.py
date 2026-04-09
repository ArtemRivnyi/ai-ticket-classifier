from flask import Blueprint, jsonify, request, Response, current_app
from datetime import datetime, timezone
import os
import logging
import socket
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/api/v1/health", methods=["GET"])
def health():
    try:
        classifier = current_app.config.get("CLASSIFIER")
        provider_status = {}
        if classifier:
            provider_status = classifier.get_status()

        return jsonify({
            "status": "healthy",
            "version": "2.5.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": os.getenv("FLASK_ENV", "development"),
            "provider_status": provider_status,
        }), 200
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({"status": "degraded", "error": str(e)}), 503

@admin_bp.route("/ready", methods=["GET"])
@admin_bp.route("/api/v1/ready", methods=["GET"])
def readiness():
    """Readiness probe ensuring environment + providers are healthy"""
    classifier = current_app.config.get("CLASSIFIER")
    env_status = current_app.config.get("ENV_STATUS")
    ALLOW_PROVIDERLESS = os.getenv("ALLOW_PROVIDERLESS", "false").lower() == "true"
    
    providers_available = False
    provider_status = {}
    if classifier:
        provider_status = classifier.get_status()
        providers_available = any(
            status == "available" for status in provider_status.values()
        )
    
    status_ok = (env_status.is_valid if env_status else True) and (providers_available or ALLOW_PROVIDERLESS)
    response_status = 200 if status_ok else 503

    return jsonify({
        "status": "ready" if status_ok else "not_ready",
        "env_valid": env_status.is_valid if env_status else True,
        "providers": provider_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }), response_status

@admin_bp.route("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
