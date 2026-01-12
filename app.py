"""
AI Ticket Classifier - Production Ready Flask Application
Full-featured REST API with OpenAPI documentation, multi-provider support,
API key authentication, rate limiting, webhooks, and comprehensive monitoring.
"""

import sys

# Python version check - MUST be 3.12
# Skip exit during testing (pytest imports modules)
_is_testing = "pytest" in sys.modules or any("pytest" in arg for arg in sys.argv)

if sys.version_info[:2] not in [(3, 12), (3, 14)]:
    try:
        print("=" * 70)
        print("ERROR: Python 3.12 is REQUIRED for this project")
        print("=" * 70)
        print(f"Current version: {sys.version}")
        print(f"Required: Python 3.12.x")
        print()
        print("Please use Python 3.12. Run: python check_python_version.py")
        print("=" * 70)
    except UnicodeEncodeError:
        # Fallback for Windows console encoding issues
        print("=" * 70)
        print("ERROR: Python 3.12 is REQUIRED for this project")
        print("=" * 70)
        print(f"Current version: {sys.version}")
        print(f"Required: Python 3.12.x")
        print()
        print("Please use Python 3.12. Run: python check_python_version.py")
        print("=" * 70)
    if not _is_testing:
        sys.exit(1)

import os
import time
import re
from uuid import uuid4
from datetime import datetime, timezone
from typing import Dict, List, Optional
import json
import bleach

from flask import (
    Flask,
    request,
    jsonify,
    Response,
    g,
    current_app,
    send_from_directory,
    render_template,
)
from flask_cors import CORS
from utils.errors import APIError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_swagger_ui import get_swaggerui_blueprint
from pydantic import BaseModel, Field, ValidationError, EmailStr, field_validator
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from dotenv import load_dotenv

load_dotenv()


# Structured logging setup
from config.logging_config import setup_logging, logger as structured_logger

setup_logging()
logger = structured_logger.bind(component="app")

import jwt

from config.env_validation import validate_environment
from config.settings import get_settings

try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration

    sentry_available = True
except ImportError:
    sentry_available = False

# Initialize Sentry if DSN is provided and module is available
settings = get_settings()
if settings.SENTRY_DSN and sentry_available:
    if _is_testing:
        print("⚠️  Sentry initialization skipped during tests")
    else:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            environment=settings.ENV,
        )
elif settings.SENTRY_DSN and not sentry_available:
    logger.warning("⚠️ SENTRY_DSN set but sentry_sdk module not found")


# Validate environment configuration
env_status = validate_environment(skip_failure=_is_testing)
ALLOW_PROVIDERLESS = os.getenv("ALLOW_PROVIDERLESS", "false").lower() == "true"
for warning in env_status.warnings:
    logger.warning(warning)

if not env_status.is_valid:
    import sys

    print(
        f"CRITICAL: Missing required environment variables: {env_status.missing}",
        file=sys.stderr,
    )
    sys.stderr.flush()
    logger.error("Missing required environment variables", missing=env_status.missing)
    if not _is_testing:
        sys.exit(1)

REQUEST_ID_HEADER = "X-Request-ID"

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-in-production")


# CORS configuration for production
settings = get_settings()
allowed_origins = settings.cors_origins_list()
if not allowed_origins:
    allowed_origins = ["*"]

CORS(
    app,
    origins=allowed_origins,
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
    supports_credentials=True,
)

# Initialize rate limiter with fallback to memory storage
# Initialize rate limiter with fallback to memory storage
try:
    from middleware.rate_limit import get_rate_limit_key
except ImportError:
    # Fallback if file not found (though it should be there)
    def get_rate_limit_key():
        return get_remote_address()


from config.redis_config import get_redis_pool

# Configure rate limiter with Redis storage
settings = get_settings()
redis_url = settings.REDIS_URL

# Suppress Flask-Limiter warning by configuring storage from the start
import warnings

warnings.filterwarnings(
    "ignore", message=".*in-memory storage.*", module="flask_limiter"
)

redis_available = False
try:
    # Use connection pool for check
    pool = get_redis_pool()
    import redis

    redis_client_test = redis.Redis(connection_pool=pool)
    redis_client_test.ping()
    redis_available = True
    logger.info(
        f"✅ Redis available at {redis_url.split('@')[-1] if '@' in redis_url else redis_url}"
    )

    # Use Redis storage with error handling
    limiter = Limiter(
        app=app,
        key_func=get_rate_limit_key,
        storage_uri=redis_url,
        default_limits=["1000 per day", "100 per hour"],
        strategy="fixed-window",
        headers_enabled=True,
        storage_options={
            "socket_connect_timeout": 1,
            "socket_timeout": 1,
            "retry_on_timeout": False,
            "health_check_interval": 30,
        },
    )
    logger.info("✅ Rate limiter configured with Redis storage")
except Exception as e:
    logger.warning(
        f"⚠️ Redis not available, using in-memory storage for rate limiting: {e}"
    )
    redis_available = False
    limiter = Limiter(
        app=app,
        key_func=get_rate_limit_key,
        default_limits=["1000 per day", "100 per hour"],
        strategy="fixed-window",
        headers_enabled=True,
    )

if redis_available:
    cache_config = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_REDIS_URL": redis_url,
        "CACHE_DEFAULT_TIMEOUT": 300,
    }
    logger.info("✅ Cache configured with Redis")
else:
    cache_config = {"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 300}
    logger.info("ℹ️ Cache configured with SimpleCache (fallback)")

cache = Cache(app, config=cache_config)

# Import providers and middleware
try:
    from providers.multi_provider import MultiProvider

    classifier = MultiProvider()
    if classifier.gemini_available or classifier.openai_available:
        logger.info("✅ Multi-Provider system initialized")
    else:
        logger.warning("⚠️ Multi-Provider initialized but no providers available")
    app.config["CLASSIFIER"] = classifier
except Exception as e:
    error_str = str(e).lower()
    if "metaclass" in error_str or "tp_new" in error_str:
        logger.warning(
            f"⚠️ Provider initialization issue (Python version compatibility): {e}"
        )
        logger.warning("⚠️ Application will run but classification may not work")
    else:
        logger.error(f"❌ Failed to initialize provider: {e}")
    classifier = None
    app.config["CLASSIFIER"] = None

try:
    from middleware.auth import (
        require_api_key,
        optional_api_key,
        APIKeyManager,
        RateLimiter,
    )

    logger.info("✅ Auth middleware loaded")
except Exception as e:
    logger.error(f"⚠️ Auth middleware not available: {e}")
    require_api_key = lambda f: f
    optional_api_key = lambda f: f
    APIKeyManager = None
    RateLimiter = None

try:
    from security.jwt_auth import require_jwt_or_api_key

    logger.info("✅ JWT auth loaded")
except Exception as e:
    logger.warning(f"⚠️ JWT auth not available: {e}")
    require_jwt_or_api_key = require_api_key  # Fallback to API key only

try:
    from api.auth import auth_bp

    app.register_blueprint(auth_bp)
    logger.info("✅ Auth blueprint registered")
except Exception as e:
    logger.warning(f"⚠️ Auth blueprint not available: {e}")

try:
    from monitoring.metrics import (
        request_count,
        request_duration,
        classification_count,
        error_count,
        active_requests,
        # NEW: Analytics metrics
        classification_accuracy,
        category_distribution,
        subcategory_distribution,
        provider_usage,
        classification_errors,
    )

    logger.info("✅ Metrics initialized")
except Exception as e:
    logger.warning(f"⚠️ Metrics not available: {e}")
    request_count = None
    request_duration = None
    classification_count = None
    error_count = None
    active_requests = None
    classification_accuracy = None
    category_distribution = None
    subcategory_distribution = None
    provider_usage = None
    classification_errors = None

try:
    from api.integrations import integrations_bp

    app.register_blueprint(integrations_bp)
    logger.info("✅ Integrations blueprint registered")
except Exception as e:
    logger.warning(f"⚠️ Integrations blueprint not available: {e}")

try:
    from api.feedback import feedback_bp

    app.register_blueprint(feedback_bp)
    logger.info("✅ Feedback blueprint registered")
except Exception as e:
    logger.warning(f"⚠️ Feedback blueprint not available: {e}")

# Swagger UI Configuration
SWAGGER_URL = "/docs"
API_URL = "/static/swagger.json"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "AI Ticket Classifier API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# ===== PYDANTIC MODELS =====


class TicketRequest(BaseModel):
    ticket: str = Field(..., min_length=10, max_length=5000)


class FeedbackRequest(BaseModel):
    request_id: str
    correct: bool
    ticket: Optional[str] = None
    predicted: Optional[str] = None
    comments: Optional[str] = None


# ===== ROUTES =====


@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html", demo_api_key=os.getenv("MASTER_API_KEY"))


@app.route("/about")
def about():
    """Render the about page."""
    return render_template("about.html")


@app.route("/evaluation")
def evaluation():
    """Render the evaluation page."""
    return render_template("evaluation.html")


@app.route("/api/v1/evaluation-results")
def evaluation_results():
    """Serve the evaluation results JSON."""
    try:
        with open("evaluation_results.json", "r") as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return (
            jsonify(
                {"error": "Evaluation results not found. Run evaluate_model.py first."}
            ),
            404,
        )


@app.route("/api/evaluation/run", methods=["POST"])
@optional_api_key
@limiter.limit("5 per minute")
def run_evaluation():
    """Run the evaluation and return results."""
    try:
        import csv
        import time

        results = []
        correct_count = 0
        total_count = 0

        with open("test_dataset.csv", "r") as f:
            reader = csv.DictReader(f)
            tickets = list(reader)
            total_count = len(tickets)

            for i, ticket in enumerate(tickets):
                text = ticket["text"]
                expected_category = ticket["expected_category"]
                expected_priority = ticket["expected_priority"]

                try:
                    start_time = time.time()
                    result = classifier.classify(text)
                    latency = time.time() - start_time

                    predicted_category = result.get("category", "Unknown")
                    predicted_priority = result.get("priority", "unknown")
                    confidence = result.get("confidence", 0.0)

                    # Only check category for accuracy (priority is informational)
                    is_correct = predicted_category == expected_category

                    if is_correct:
                        correct_count += 1

                    results.append(
                        {
                            "ticket": text,
                            "expected_category": expected_category,
                            "expected_priority": expected_priority,
                            "predicted_category": predicted_category,
                            "predicted_priority": predicted_priority,
                            "confidence": confidence,
                            "correct": is_correct,
                            "latency": round(latency, 3),
                            "provider": result.get("provider", "unknown"),
                        }
                    )
                except Exception as e:
                    logger.error(f"Error evaluating ticket {i}: {e}")
                    results.append(
                        {
                            "ticket": text,
                            "expected_category": expected_category,
                            "expected_priority": expected_priority,
                            "predicted_category": "Error",
                            "predicted_priority": "unknown",
                            "confidence": 0.0,
                            "correct": False,
                            "latency": 0,
                            "provider": "error",
                            "error": str(e),
                        }
                    )

        accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
        avg_latency = (
            sum(r["latency"] for r in results) / len(results) if results else 0
        )

        output = {
            "accuracy": round(accuracy, 2),
            "total": total_count,
            "correct": correct_count,
            "incorrect": total_count - correct_count,
            "avg_latency": round(avg_latency, 3),
            "results": results,
        }

        # Save results
        with open("evaluation_results.json", "w") as f:
            json.dump(output, f, indent=2)

        return jsonify(output), 200

    except FileNotFoundError:
        return (
            jsonify(
                {
                    "error": "Test dataset not found. Please ensure test_dataset.csv exists."
                }
            ),
            404,
        )
    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/feedback", methods=["POST"])
@app.route("/api/feedback", methods=["POST"])
@limiter.limit("10 per minute")
def submit_feedback():
    """Submit feedback for a classification result."""
    try:
        json_data = request.get_json(silent=True)
        if json_data is None:
            return jsonify({"error": "Request must be JSON or valid JSON"}), 400

        data = FeedbackRequest(**json_data)

        feedback_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": data.request_id,
            "correct": data.correct,
            "ticket": data.ticket,
            "predicted": data.predicted,
            "comments": data.comments,
        }

        # Append to local file (simple storage for MVP)
        feedback_file = "feedback.json"
        existing_feedback = []

        if os.path.exists(feedback_file):
            try:
                with open(feedback_file, "r") as f:
                    existing_feedback = json.load(f)
            except json.JSONDecodeError:
                pass  # Start fresh if corrupted

        existing_feedback.append(feedback_entry)

        with open(feedback_file, "w") as f:
            json.dump(existing_feedback, f, indent=2)

        return jsonify({"status": "success", "message": "Feedback received"}), 200

    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.errors()}), 400
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        return jsonify({"error": str(e)}), 500


# ===== PYDANTIC MODELS =====


class TicketRequest(BaseModel):
    """Request model for single ticket classification"""

    ticket: str = Field(
        ..., min_length=1, max_length=5000, description="Ticket text to classify"
    )

    @field_validator("ticket")
    @classmethod
    def sanitize_ticket(cls, v):
        """Sanitize ticket text - remove potentially harmful content"""
        # Remove null bytes
        v = v.replace("\x00", "")
        # Use bleach to clean HTML
        v = bleach.clean(v, strip=True)
        # Remove excessive whitespace
        v = re.sub(r"\s+", " ", v)
        # Limit to 5000 characters
        return v[:5000].strip()


class BatchTicketRequest(BaseModel):
    """Request model for batch classification"""

    tickets: List[str] = Field(
        ..., min_length=1, max_length=100, description="List of tickets to classify"
    )
    webhook_url: Optional[str] = Field(
        None, description="Optional webhook URL for async results"
    )

    @field_validator("tickets")
    @classmethod
    def sanitize_tickets(cls, v):
        """Sanitize batch tickets"""
        return [
            re.sub(r"\s+", " ", ticket.replace("\x00", ""))[:5000].strip()
            for ticket in v
            if ticket.strip()
        ]


class WebhookConfig(BaseModel):
    """Webhook configuration"""

    url: str = Field(..., description="Webhook URL")
    secret: Optional[str] = Field(None, description="Webhook secret for verification")
    events: List[str] = Field(
        default=["classification.completed"], description="Events to subscribe to"
    )


# ===== HELPER FUNCTIONS =====


def clean_text(text: str) -> str:
    """
    Clean text by removing email signatures, forwarded headers, and common noise.
    """
    if not text:
        return ""

    # Remove "Begin forwarded message" blocks
    text = re.sub(
        r"-+\s*Forwarded message\s*-+.*", "", text, flags=re.IGNORECASE | re.DOTALL
    )
    text = re.sub(
        r"From:.*Sent:.*To:.*Subject:.*", "", text, flags=re.IGNORECASE | re.DOTALL
    )

    # Remove common signature separators
    text = re.sub(r"(?m)^--\s*$.*", "", text, flags=re.DOTALL)
    text = re.sub(r"(?m)^__\s*$.*", "", text, flags=re.DOTALL)

    # Remove "Sent from my iPhone" etc.
    text = re.sub(r"(?m)^Sent from my.*$", "", text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(
        r"(?m)^Get Outlook for.*$", "", text, flags=re.IGNORECASE | re.MULTILINE
    )

    return text.strip()


def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    if not text:
        return ""

    # First, clean noise (signatures, etc.)
    text = clean_text(text)

    # Remove null bytes
    text = text.replace("\x00", "")
    # Use bleach to clean HTML
    text = bleach.clean(text, strip=True)
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)
    # Limit length
    return text[:5000].strip()


def get_user_tier() -> str:
    """Get user tier from request context"""
    return getattr(request, "api_key_tier", "free")


def get_rate_limit() -> str:
    """Get rate limit string based on tier"""
    tier = get_user_tier()
    tier_limits = {
        "free": "100 per hour; 10 per minute",
        "starter": "1000 per hour",
        "professional": "10000 per hour",
        "enterprise": "100000 per hour",
    }
    return tier_limits.get(tier, tier_limits["free"])


def include_request_id(payload: Dict) -> Dict:
    """Attach request_id to payload if available"""
    if not isinstance(payload, dict):
        return payload
    data = dict(payload)
    request_id = getattr(g, "request_id", None)
    if request_id and "request_id" not in data:
        data["request_id"] = request_id
    return data


def make_response(payload: Dict, status_code: int = 200):
    """Convenience helper for JSON responses with request IDs"""
    return jsonify(include_request_id(payload)), status_code


def get_trace_logger():
    """Return a logger bound with trace/request context"""
    return getattr(g, "trace_logger", logger)


# ===== MIDDLEWARE =====


@app.before_request
def before_request():
    """Pre-request processing"""
    incoming_request_id = request.headers.get(REQUEST_ID_HEADER) or request.headers.get(
        "X-Correlation-ID"
    )
    g.request_id = incoming_request_id or f"req_{uuid4().hex}"
    g.trace_logger = logger.bind(
        trace_id=g.request_id, path=request.path, method=request.method
    )

    request.start_time = time.time()

    # Record active requests
    if active_requests:
        active_requests.inc()

    # Force HTTPS in production (if configured)
    settings = get_settings()
    if settings.FORCE_HTTPS and not current_app.testing:
        forwarded_proto = request.headers.get("X-Forwarded-Proto", "").lower()
        if forwarded_proto != "https" and not request.is_secure:
            return jsonify(include_request_id({"error": "HTTPS required"})), 403

    # Log request
    g.trace_logger.info("request_received")


@app.after_request
def after_request(response):
    """Post-request processing"""
    # Record active requests
    if active_requests:
        active_requests.dec()

    # Record metrics (only if start_time was set in before_request)
    if request_count and request_duration and hasattr(request, "start_time"):
        duration = time.time() - request.start_time

        endpoint = request.endpoint or request.path
        method = request.method
        status = response.status_code

        request_count.labels(method=method, endpoint=endpoint, status=status).inc()
        request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Content Security Policy - Allow Tailwind CDN (unsafe-eval) and other resources
    csp = (
        "default-src 'self' https:; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; "
        "style-src 'self' 'unsafe-inline' https:; "
        "img-src 'self' data: https:; "
        "font-src 'self' https: data:; "
        "connect-src 'self' https:;"
    )
    response.headers["Content-Security-Policy"] = csp

    if os.getenv("FORCE_HTTPS", "false").lower() == "true":
        response.headers[
            "Strict-Transport-Security"
        ] = "max-age=31536000; includeSubDomains"

    response.headers[REQUEST_ID_HEADER] = getattr(g, "request_id", "unknown")

    return response


# ===== ROOT ENDPOINT =====


@app.route("/api", methods=["GET"])
@limiter.exempt
def root():
    """Root endpoint with API information"""
    return make_response(
        {
            "message": "AI Ticket Classifier API",
            "version": "2.2.0",
            "docs": "/api-docs",
        },
        200,
    )


# ===== HEALTH & STATUS ENDPOINTS =====


@app.route("/api/v1/health", methods=["GET"])
@limiter.exempt
def health():
    try:
        provider_status = {}
        if classifier:
            provider_status = classifier.get_status()

        return make_response(
            {
                "status": "healthy",
                "version": "2.5.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "environment": os.getenv("FLASK_ENV", "development"),
                "provider_status": provider_status,
            },
            200,
        )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return make_response({"status": "degraded", "error": str(e)}, 503)


@app.route("/ready", methods=["GET"])
@app.route("/api/v1/ready", methods=["GET"])
@limiter.exempt
@optional_api_key
def readiness():
    """Readiness probe ensuring environment + providers are healthy"""
    providers_available = False
    provider_status = {}
    if classifier:
        provider_status = classifier.get_status()
        providers_available = any(
            status == "available" for status in provider_status.values()
        )
    status_ok = env_status.is_valid and (providers_available or ALLOW_PROVIDERLESS)
    response_status = 200 if status_ok else 503

    return make_response(
        {
            "status": "ready" if status_ok else "not_ready",
            "env_valid": env_status.is_valid,
            "warnings": env_status.warnings,
            "providers": provider_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        response_status,
    )


@app.route("/api/v1/status", methods=["GET"])
@require_api_key
def status():
    """Get detailed status including provider health"""
    try:
        if not classifier:
            return make_response(
                {
                    "error": "Classification service unavailable",
                    "message": "AI provider not initialized. Please check GEMINI_API_KEY or OPENAI_API_KEY",
                },
                503,
            )

        # Check if any provider is available
        if (
            not ALLOW_PROVIDERLESS
            and hasattr(classifier, "gemini_available")
            and hasattr(classifier, "openai_available")
        ):
            if not classifier.gemini_available and not classifier.openai_available:
                return make_response(
                    {
                        "error": "No AI providers available",
                        "message": "Please configure GEMINI_API_KEY or OPENAI_API_KEY",
                    },
                    503,
                )

        return make_response(
            {
                "status": "operational",
                "providers": classifier.get_status(),
                "api_version": "2.3.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            200,
        )
    except Exception as e:
        logger.error(f"Status error: {e}")
        return make_response({"error": str(e)}, 500)


@app.route("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


# ===== CLASSIFICATION ENDPOINTS =====


@app.route("/api/v1/classify", methods=["POST"])
@require_api_key
@limiter.limit(get_rate_limit)
def classify():
    # Custom cache key generator based on ticket text
    def make_cache_key(*args, **kwargs):
        if request.is_json and request.json and "ticket" in request.json:
            return f"classify:{request.json['ticket']}"
        return None

    # Check cache manually to handle the response object correctly
    if request.is_json and request.json and "ticket" in request.json:
        cache_key = f"classify:{request.json['ticket']}"
        cached_response = cache.get(cache_key)
        if cached_response:
            logger.info("✅ Cache hit for classification")
            # If cached response is a dict, wrap it
            if isinstance(cached_response, dict):
                return make_response(cached_response)
            return cached_response

    start_time = time.time()
    trace_logger = get_trace_logger()

    try:
        # Check if request has JSON
        if not request.is_json:
            if error_count:
                error_count.labels(error_type="validation_error").inc()
            return make_response(
                {"error": "Invalid request", "message": "Request must be JSON"}, 400
            )

        # Validate request
        try:
            if request.json is None:
                raise ValueError("JSON body is required")
            data = TicketRequest(**request.json)
        except (ValidationError, ValueError, TypeError) as e:
            if error_count:
                error_count.labels(error_type="validation_error").inc()
            if isinstance(e, ValidationError):
                return make_response(
                    {"error": "Validation error", "details": e.errors()}, 400
                )
            else:
                return make_response(
                    {
                        "error": "Invalid request",
                        "message": str(e)
                        if str(e)
                        else "Invalid JSON or missing required fields",
                    },
                    400,
                )
        except Exception as e:
            # Handle JSON decode errors
            if error_count:
                error_count.labels(error_type="validation_error").inc()
            return make_response(
                {
                    "error": "Invalid JSON",
                    "message": "Failed to parse JSON. Please check your request format.",
                },
                400,
            )

        # Sanitize input
        ticket = sanitize_input(data.ticket)
        if not ticket:
            return make_response({"error": "Ticket cannot be empty"}, 400)

        # Classify
        if not classifier:
            return make_response(
                {
                    "error": "Classification service unavailable",
                    "message": "AI provider not initialized. Please check GEMINI_API_KEY or OPENAI_API_KEY",
                },
                503,
            )

        # Check if any provider is available
        if (
            not ALLOW_PROVIDERLESS
            and hasattr(classifier, "gemini_available")
            and hasattr(classifier, "openai_available")
        ):
            if not classifier.gemini_available and not classifier.openai_available:
                return make_response(
                    {
                        "error": "No AI providers available",
                        "message": "Please configure GEMINI_API_KEY or OPENAI_API_KEY",
                    },
                    503,
                )

        result = classifier.classify(ticket)

        # Cache the result
        if request.is_json and request.json and "ticket" in request.json:
            cache_key = f"classify:{request.json['ticket']}"
            cache.set(cache_key, result, timeout=3600)  # Cache for 1 hour

        # Record existing metrics
        if classification_count:
            classification_count.labels(
                category=result.get("category", "unknown"),
                provider=result.get("provider", "unknown"),
                status="success",
            ).inc()

        # NEW: Record analytics metrics
        if classification_accuracy and "confidence" in result:
            classification_accuracy.observe(result["confidence"])

        if category_distribution and "category" in result:
            category_distribution.labels(category=result["category"]).inc()

        if subcategory_distribution and "subcategory" in result:
            subcategory_distribution.labels(
                category=result.get("category", "unknown"),
                subcategory=result.get("subcategory", "unknown"),
            ).inc()

        if provider_usage and "provider" in result:
            provider_usage.labels(provider=result["provider"]).inc()

        duration = time.time() - start_time
        result["processing_time"] = round(duration, 2)

        trace_logger.info(
            "classification_success",
            category=result.get("category"),
            provider=result.get("provider"),
            duration=duration,
        )

        return make_response(result, 200)

    except Exception as e:
        trace_logger.error("classification_error", error=str(e))
        if error_count:
            error_count.labels(error_type="classification_error").inc()
        if classification_errors:
            classification_errors.labels(error_type="internal_error").inc()
        return make_response(
            {
                "error": "Internal server error",
                "message": str(e)
                if os.getenv("FLASK_ENV") == "development"
                else "An error occurred",
            },
            500,
        )


@app.route("/api/v1/batch", methods=["POST"])
@require_api_key
@limiter.limit(get_rate_limit)
def batch_classify():
    start_time = time.time()
    trace_logger = get_trace_logger()

    try:
        # Validate request
        try:
            data = BatchTicketRequest(**request.json)
        except ValidationError as e:
            if error_count:
                error_count.labels(error_type="validation_error").inc()
            return make_response(
                {"error": "Validation error", "details": e.errors()}, 400
            )

        # Check batch size limit based on tier
        tier = get_user_tier()
        max_batch = {
            "free": 10,
            "starter": 50,
            "professional": 100,
            "enterprise": 1000,
        }.get(tier, 10)

        if len(data.tickets) > max_batch:
            return make_response(
                {
                    "error": f"Batch size exceeds limit for tier {tier}. Maximum: {max_batch}"
                },
                400,
            )

        # Sanitize tickets
        tickets = [sanitize_input(t) for t in data.tickets]
        tickets = [t for t in tickets if t]  # Remove empty

        if not tickets:
            return make_response({"error": "No valid tickets provided"}, 400)

        # Classify all tickets
        if not classifier:
            return make_response(
                {
                    "error": "Classification service unavailable",
                    "message": "AI provider not initialized. Please check GEMINI_API_KEY or OPENAI_API_KEY",
                },
                503,
            )

        # Check if any provider is available
        if (
            not ALLOW_PROVIDERLESS
            and hasattr(classifier, "gemini_available")
            and hasattr(classifier, "openai_available")
        ):
            if not classifier.gemini_available and not classifier.openai_available:
                return make_response(
                    {
                        "error": "No AI providers available",
                        "message": "Please configure GEMINI_API_KEY or OPENAI_API_KEY",
                    },
                    503,
                )

        results = []
        errors = []

        for i, ticket in enumerate(tickets):
            try:
                result = classifier.classify(ticket)
                results.append(result)

                # Record metrics
                if classification_count:
                    classification_count.labels(
                        category=result.get("category", "unknown"),
                        provider=result.get("provider", "unknown"),
                        status="success",
                    ).inc()

            except Exception as e:
                logger.error(f"Error classifying ticket {i}: {e}")
                errors.append(
                    {"index": i, "ticket": ticket[:50] + "...", "error": str(e)}
                )

        duration = time.time() - start_time

        return make_response(
            {
                "total": len(tickets),
                "successful": len(results),
                "failed": len(errors),
                "results": results,
                "errors": errors,
                "processing_time": round(duration, 2),
            },
            200,
        )

    except Exception as e:
        trace_logger.error("batch_classification_error", error=str(e))
        return make_response({"error": "Internal server error", "message": str(e)}, 500)


@app.route("/api/v1/classify/batch-csv", methods=["POST"])
@require_api_key
@limiter.limit(get_rate_limit)
def batch_classify_csv():
    """Handle CSV file upload for batch classification"""
    start_time = time.time()
    trace_logger = get_trace_logger()

    try:
        if "file" not in request.files:
            return make_response({"error": "No file part"}, 400)

        file = request.files["file"]
        if file.filename == "":
            return make_response({"error": "No selected file"}, 400)

        if not file.filename.endswith(".csv"):
            return make_response({"error": "File must be a CSV"}, 400)

        try:
            import pandas as pd
        except ImportError:
            logger.error("Pandas not installed")
            return make_response(
                {"error": "Server configuration error: pandas not installed"}, 500
            )

        try:
            df = pd.read_csv(file)
        except Exception as e:
            return make_response({"error": f"Invalid CSV file: {str(e)}"}, 400)

        # Check for 'ticket' column (case insensitive)
        ticket_col = None
        # Prioritize 'text' and 'description' over 'ticket' (which might be an ID)
        priority_cols = [
            "text",
            "summary",
            "description",
            "ticket",
            "content",
            "body",
            "issue",
        ]

        columns_lower = {col.lower(): col for col in df.columns}

        for priority in priority_cols:
            if priority in columns_lower:
                ticket_col = columns_lower[priority]
                break

        if not ticket_col:
            return make_response(
                {
                    "error": 'CSV must contain a "text", "description", or "ticket" column'
                },
                400,
            )

        # Limit rows based on tier
        tier = get_user_tier()
        max_rows = {
            "free": 10,
            "starter": 50,
            "professional": 100,
            "enterprise": 1000,
        }.get(tier, 10)

        if len(df) > max_rows:
            return make_response(
                {"error": f"Row limit exceeded for {tier} tier. Max: {max_rows}"}, 400
            )

        tickets = df[ticket_col].astype(str).tolist()
        tickets = [sanitize_input(t) for t in tickets if t and str(t).strip()]

        if not tickets:
            return make_response({"error": "No valid tickets found in CSV"}, 400)

        # Reuse existing batch logic or call classifier directly
        if not classifier:
            return make_response(
                {
                    "error": "Classification service unavailable",
                    "message": "AI provider not initialized",
                },
                503,
            )

        results = []
        errors = []

        for i, ticket in enumerate(tickets):
            try:
                result = classifier.classify(ticket)
                results.append(result)

                # Record metrics
                if classification_count:
                    classification_count.labels(
                        category=result.get("category", "unknown"),
                        provider=result.get("provider", "unknown"),
                        status="success",
                    ).inc()
            except Exception as e:
                logger.error(f"Error classifying CSV ticket {i}: {e}")
                errors.append(
                    {"index": i, "ticket": ticket[:50] + "...", "error": str(e)}
                )

        duration = time.time() - start_time

        return make_response(
            {
                "total": len(tickets),
                "successful": len(results),
                "failed": len(errors),
                "results": results,
                "errors": errors,
                "processing_time": round(duration, 2),
            },
            200,
        )

    except Exception as e:
        trace_logger.error("batch_classification_error", error=str(e))
        if error_count:
            error_count.labels(error_type="batch_error").inc()
        return make_response(
            {
                "error": "Internal server error",
                "message": str(e)
                if os.getenv("FLASK_ENV") == "development"
                else "An error occurred",
            },
            500,
        )


# ===== FEEDBACK ENDPOINT =====


# ===== ERROR HANDLERS =====


@app.errorhandler(400)
def bad_request(e):
    """Handle 400 Bad Request errors"""
    return make_response(
        {
            "error": "Bad request",
            "message": str(e.description)
            if hasattr(e, "description")
            else "Invalid request",
        },
        400,
    )


@app.errorhandler(404)
def not_found(e):
    """Handle 404 Not Found errors"""
    return make_response(
        {
            "error": "Not found",
            "message": "The requested resource was not found",
            "path": request.path,
        },
        404,
    )


@app.errorhandler(429)
def rate_limit_exceeded(e):
    """Handle 429 Rate Limit Exceeded errors"""
    return make_response(
        {
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
        },
        429,
    )


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 Internal Server Error"""
    logger.error(f"Internal server error: {e}")
    return make_response(
        {"error": "Internal server error", "message": "An unexpected error occurred"},
        500,
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "production") == "development"

    logger.info(f"🚀 Starting AI Ticket Classifier API on port {port}")
    logger.info(f"Environment: {os.getenv('FLASK_ENV', 'production')}")

    app.run(host="0.0.0.0", port=port, debug=debug)
