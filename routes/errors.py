from flask import Blueprint, make_response, jsonify, request, current_app
import os
import logging
from utils.errors import APIError

logger = logging.getLogger(__name__)

errors_bp = Blueprint("errors", __name__)

@errors_bp.app_errorhandler(400)
def bad_request(e):
    return make_response(jsonify({
        "error": "Bad request",
        "message": str(e.description) if hasattr(e, "description") else "Invalid request"
    }), 400)

@errors_bp.app_errorhandler(404)
def not_found(e):
    return make_response(jsonify({
        "error": "Not found",
        "message": "The requested resource was not found",
        "path": request.path
    }), 404)

@errors_bp.app_errorhandler(429)
def rate_limit_exceeded(e):
    return make_response(jsonify({
        "error": "Rate limit exceeded",
        "message": "Too many requests. Please try again later."
    }), 429)

@errors_bp.app_errorhandler(APIError)
def handle_api_error(e):
    return make_response(jsonify(e.to_dict()), e.status_code)

@errors_bp.app_errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {e}")
    return make_response(jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500)
