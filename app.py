from flask import Flask, request, jsonify, g
from classify import classify_ticket
import logging
from logging.handlers import RotatingFileHandler
import os
import traceback
import time
import uuid
from functools import wraps
from pydantic import BaseModel, ValidationError, Field
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram

# Import Redis modules
from rate_limiter import rate_limit, rate_limiter
from cache_manager import cache_manager

app = Flask(__name__)

# ===== Prometheus Metrics =====
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'AI Ticket Classifier', version='1.0.0')

# Custom metrics
classification_counter = Counter(
    'classifications_total', 
    'Total classifications',
    ['category', 'status']
)

classification_duration = Histogram(
    'classification_duration_seconds',
    'Classification duration',
    ['category']
)

api_errors = Counter(
    'api_errors_total',
    'Total API errors',
    ['error_type']
)

cache_hits = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['result']
)

# ===== Logging setup =====
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "app.log")

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    def format(self, record):
        import json
        from datetime import datetime
        
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add request ID if available
        if hasattr(g, 'request_id'):
            log_data['request_id'] = g.request_id
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
            
        return json.dumps(log_data)

handler = RotatingFileHandler(
    LOG_PATH, 
    maxBytes=5_000_000,  # 5MB
    backupCount=10, 
    encoding="utf-8"
)
handler.setFormatter(JSONFormatter())

# Console handler with simple format
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
console_handler.setFormatter(console_formatter)

# Root logger settings
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Clear existing handlers to avoid duplicates
root_logger.handlers.clear()
root_logger.addHandler(handler)
root_logger.addHandler(console_handler)

app.logger = root_logger.getChild("ai-ticket-classifier")

# ===== Configuration =====
API_KEY = os.getenv("API_KEY")

# ===== Request tracking =====
@app.before_request
def before_request():
    """Track request ID and start time"""
    g.request_id = str(uuid.uuid4())
    g.start_time = time.time()

@app.after_request
def after_request(response):
    """Log request completion"""
    if hasattr(g, 'request_id'):
        response.headers['X-Request-ID'] = g.request_id
        
        # Log request details
        if hasattr(g, 'start_time'):
            duration = (time.time() - g.start_time) * 1000
            app.logger.info(
                "Request completed",
                extra={
                    'extra_data': {
                        'request_id': g.request_id,
                        'method': request.method,
                        'path': request.path,
                        'status_code': response.status_code,
                        'duration_ms': round(duration, 2),
                        'ip': request.remote_addr,
                        'user_agent': request.headers.get('User-Agent', 'Unknown')
                    }
                }
            )
    return response

# ===== Authentication decorator =====
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip auth check if API_KEY not configured
        if not API_KEY:
            app.logger.warning("API_KEY not configured - authentication disabled")
            return f(*args, **kwargs)
        
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            app.logger.warning(
                "Missing API key in request",
                extra={'extra_data': {'request_id': g.request_id if hasattr(g, 'request_id') else None}}
            )
            api_errors.labels(error_type='missing_api_key').inc()
            return make_error("Missing API key", 401, "Provide X-API-Key header")
        
        if api_key != API_KEY:
            app.logger.warning(
                "Invalid API key attempt",
                extra={'extra_data': {'request_id': g.request_id if hasattr(g, 'request_id') else None}}
            )
            api_errors.labels(error_type='invalid_api_key').inc()
            return make_error("Invalid API key", 401)
        
        return f(*args, **kwargs)
    return decorated_function

# ===== Helpers =====
def make_error(message: str, code: int = 500, details: str | None = None):
    body = {
        "error": message,
        "code": code
    }
    if details:
        body["details"] = details
    if hasattr(g, 'request_id'):
        body["request_id"] = g.request_id
    return jsonify(body), code

# ===== Pydantic models =====
class TicketInput(BaseModel):
    ticket: str = Field(..., min_length=1, max_length=5000, description="Support ticket text")
    priority: str | None = Field(None, pattern="^(low|medium|high|critical)$")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticket": "I cannot connect to the VPN",
                "priority": "high"
            }
        }

class ClassificationResponse(BaseModel):
    category: str
    priority: str
    processing_time_ms: float | None = None
    confidence: float | None = None
    request_id: str | None = None
    cached: bool | None = False

# ===== Health endpoint =====
@app.route("/api/v1/health", methods=["GET"])
def health():
    """
    Health check endpoint
    Returns service status and basic info
    """
    app.logger.info("Health check called")
    
    # Check Redis connection
    redis_status = "connected" if rate_limiter.is_available() and cache_manager.enabled else "disconnected"
    
    return jsonify({
        "status": "ok",
        "service": "AI Ticket Classifier",
        "version": "1.0.0",
        "timestamp": time.time(),
        "uptime_seconds": time.time() - app.config.get('START_TIME', time.time()),
        "redis": {
            "status": redis_status,
            "rate_limiter": rate_limiter.is_available(),
            "cache": cache_manager.enabled
        }
    }), 200

# ===== Classification endpoint with Redis Rate Limiting & Caching =====
@app.route("/api/v1/classify", methods=["POST"])
@require_api_key
@rate_limit(limit=100, window=3600)  # 100 requests per hour
def classify():
    """
    Classify a support ticket with Redis caching
    
    Request body:
    {
        "ticket": "Support ticket text",
        "priority": "low|medium|high|critical" (optional)
    }
    
    Returns:
    {
        "category": "Category name",
        "priority": "medium",
        "processing_time_ms": 123.45,
        "cached": false,
        "request_id": "uuid"
    }
    """
    start_time = time.time()
    ticket_text = None
    category = None
    cached = False
    
    try:
        data = request.get_json(silent=True)
        if not data:
            app.logger.warning("Bad request - no JSON data")
            api_errors.labels(error_type='invalid_json').inc()
            return make_error("Invalid JSON", 400, "Request body must be valid JSON")
        
        # Validate input using pydantic
        try:
            ticket_input = TicketInput(**data)
        except ValidationError as e:
            app.logger.warning(
                "Validation error",
                extra={'extra_data': {'errors': str(e)}}
            )
            api_errors.labels(error_type='validation_error').inc()
            return make_error("Invalid input", 400, details=str(e))
        
        ticket_text = ticket_input.ticket
        priority = ticket_input.priority or "medium"
        
        app.logger.info(
            "Received ticket for classification",
            extra={
                'extra_data': {
                    'ticket_length': len(ticket_text),
                    'priority': priority,
                    'request_id': g.request_id
                }
            }
        )
        
        # Check cache first
        cached_result = cache_manager.get(ticket_text)
        if cached_result:
            category = cached_result.get('category')
            cached = True
            cache_hits.labels(result='hit').inc()
            
            app.logger.info(
                "Cache HIT - returning cached result",
                extra={
                    'extra_data': {
                        'category': category,
                        'request_id': g.request_id
                    }
                }
            )
        else:
            cache_hits.labels(result='miss').inc()
            
            # Perform classification
            category = classify_ticket(ticket_text)
            
            if not category or category.lower() in ("error", "unknown"):
                app.logger.error(
                    f"Classification returned invalid result: {category}",
                    extra={'extra_data': {'request_id': g.request_id}}
                )
                classification_counter.labels(category='error', status='failed').inc()
                api_errors.labels(error_type='classification_failed').inc()
                return make_error(
                    "Classification failed", 
                    502, 
                    "AI service returned invalid response"
                )
            
            # Cache the result
            cache_manager.set(ticket_text, {'category': category}, ttl=3600)
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        app.logger.info(
            "Ticket classified successfully",
            extra={
                'extra_data': {
                    'category': category,
                    'priority': priority,
                    'processing_time_ms': processing_time,
                    'cached': cached,
                    'request_id': g.request_id
                }
            }
        )
        
        # Update metrics
        if not cached:
            classification_counter.labels(category=category, status='success').inc()
            classification_duration.labels(category=category).observe(processing_time / 1000)
        else:
            # For cached requests, we only update the counter, duration is not relevant
            classification_counter.labels(category=category, status='cached').inc()
        
        response = ClassificationResponse(
            category=category,
            priority=priority,
            processing_time_ms=round(processing_time, 2),
            cached=cached,
            request_id=g.request_id
        )
        
        return jsonify(response.model_dump()), 200
        
    except Exception as exc:
        tb = traceback.format_exc()
        processing_time = (time.time() - start_time) * 1000
        
        app.logger.error(
            "Unhandled exception in /api/v1/classify",
            extra={
                'extra_data': {
                    'exception': str(exc),
                    'exception_type': type(exc).__name__,
                    'processing_time_ms': processing_time,
                    'traceback': tb,
                    'request_id': g.request_id if hasattr(g, 'request_id') else None
                }
            }
        )
        
        classification_counter.labels(category='error', status='failed').inc()
        api_errors.labels(error_type='unhandled_exception').inc()
        return make_error("Internal server error", 500, details=str(exc) if app.debug else None)

# ===== Cache management endpoints =====
@app.route("/api/v1/cache/stats", methods=["GET"])
@require_api_key
def cache_stats():
    """Get cache statistics"""
    stats = cache_manager.get_stats()
    return jsonify(stats), 200

@app.route("/api/v1/cache/clear", methods=["POST"])
@require_api_key
def clear_cache():
    """Clear all cached results"""
    deleted = cache_manager.clear_all()
    app.logger.info(f"Cache cleared: {deleted} keys deleted")
    return jsonify({
        "status": "ok",
        "deleted_keys": deleted,
        "message": f"Cleared {deleted} cached entries"
    }), 200

# ===== Info endpoint =====
@app.route("/api/v1/info", methods=["GET"])
def info():
    """
    Get API information and available categories
    """
    return jsonify({
        "service": "AI Ticket Classifier",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/v1/health",
            "classify": "/api/v1/classify",
            "info": "/api/v1/info",
            "cache_stats": "/api/v1/cache/stats",
            "cache_clear": "/api/v1/cache/clear",
            "metrics": "/metrics"
        },
        "categories": [
            "Network Issue",
            "Hardware Issue",
            "Software Issue",
            "Account Problem",
            "Payment Issue",
            "Feature Request",
            "Other"
        ],
        "features": {
            "rate_limiting": {
                "enabled": rate_limiter.is_available(),
                "limit": "100 requests per hour",
                "storage": "Redis"
            },
            "caching": {
                "enabled": cache_manager.enabled,
                "ttl": "3600 seconds (1 hour)",
                "storage": "Redis"
            }
        },
        "authentication": {
            "required": bool(API_KEY),
            "method": "X-API-Key header"
        }
    }), 200

# ===== Error handlers =====
@app.errorhandler(404)
def not_found(error):
    api_errors.labels(error_type='not_found').inc()
    return make_error("Endpoint not found", 404, "Check /api/v1/info for available endpoints")

@app.errorhandler(405)
def method_not_allowed(error):
    api_errors.labels(error_type='method_not_allowed').inc()
    return make_error("Method not allowed", 405, f"Allowed methods: {request.url_rule.methods if request.url_rule else 'N/A'}")

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal server error: {error}")
    api_errors.labels(error_type='internal_error').inc()
    return make_error("Internal server error", 500)

# ===== Startup =====
app.config['START_TIME'] = time.time()

# ===== Run server =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.getenv("DEBUG", "false").lower() == "true"
    
    app.logger.info(
        "Starting Flask server",
        extra={
            'extra_data': {
                'port': port,
                'debug': debug_mode,
                'auth_enabled': bool(API_KEY),
                'redis_rate_limiter': rate_limiter.is_available(),
                'redis_cache': cache_manager.enabled
            }
        }
    )
    
    app.run(host="0.0.0.0", port=port, debug=debug_mode)