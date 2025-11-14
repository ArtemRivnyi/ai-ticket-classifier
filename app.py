from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import os
import time
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# ==========================================
# Rate Limiter Configuration with Redis
# ==========================================

def get_api_key_or_ip():
    """Get API key or IP for rate limiting"""
    api_key = request.headers.get('X-API-Key')
    if api_key:
        return f"api_key:{api_key}"
    return f"ip:{get_remote_address()}"

# Используем Redis для production, memory для development
REDIS_URL = os.getenv('REDIS_URL', 'memory://')
storage_uri = REDIS_URL if REDIS_URL != 'memory://' else 'memory://'

limiter = Limiter(
    app=app,
    key_func=get_api_key_or_ip,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=storage_uri,
    strategy="fixed-window",
    headers_enabled=True
)

# ==========================================
# Mock API Keys Database
# ==========================================

VALID_API_KEYS = {
    'test_key_12345': {
        'name': 'Test User',
        'tier': 'free',
        'rate_limit': '10 per minute',
        'active': True
    },
    'prod_key_67890': {
        'name': 'Production User',
        'tier': 'professional',
        'rate_limit': '100 per minute',
        'active': True
    }
}

# ==========================================
# Authentication Decorator
# ==========================================

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                'error': 'Missing API key',
                'message': 'Please provide X-API-Key header',
                'code': 'AUTH_001'
            }), 401
        
        if api_key not in VALID_API_KEYS:
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is not valid',
                'code': 'AUTH_002'
            }), 401
        
        key_data = VALID_API_KEYS[api_key]
        if not key_data['active']:
            return jsonify({
                'error': 'Inactive API key',
                'message': 'This API key has been deactivated',
                'code': 'AUTH_003'
            }), 401
        
        # Store key data in request context
        request.api_key_data = key_data
        
        return f(*args, **kwargs)
    
    return decorated_function

# ==========================================
# Mock Classification Function
# ==========================================

def classify_ticket_mock(ticket_text, priority=None):
    """Mock classification - replace with real Gemini API call"""
    
    # Simulate processing delay
    time.sleep(0.1)
    
    # Simple keyword-based classification for testing
    text_lower = ticket_text.lower()
    
    if any(word in text_lower for word in ['vpn', 'network', 'connection', 'internet', 'wifi']):
        return 'Network Issue', 0.95
    elif any(word in text_lower for word in ['keyboard', 'mouse', 'screen', 'hardware']):
        return 'Hardware Issue', 0.92
    elif any(word in text_lower for word in ['crash', 'error', 'bug', 'software', 'application']):
        return 'Software Issue', 0.88
    elif any(word in text_lower for word in ['password', 'login', 'account', 'access']):
        return 'Account Problem', 0.90
    elif any(word in text_lower for word in ['payment', 'billing', 'invoice', 'refund']):
        return 'Payment Issue', 0.93
    elif any(word in text_lower for word in ['feature', 'request', 'enhancement', 'add']):
        return 'Feature Request', 0.85
    else:
        return 'Other', 0.70

# ==========================================
# API Endpoints
# ==========================================

@app.route('/api/v1/health', methods=['GET'])
def health():
    """Health check endpoint"""
    # Check Redis connection
    redis_status = 'connected' if storage_uri != 'memory://' else 'not_configured'
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'AI Ticket Classifier',
        'version': '1.0.0',
        'redis': redis_status,
        'storage': storage_uri.split('://')[0]
    }), 200

@app.route('/api/v1/info', methods=['GET'])
def info():
    """Service information endpoint"""
    return jsonify({
        'service': 'AI Ticket Classifier',
        'version': '1.0.0',
        'description': 'AI-powered support ticket classification service',
        'endpoints': {
            'classify': '/api/v1/classify',
            'health': '/api/v1/health',
            'info': '/api/v1/info',
            'metrics': '/metrics'
        },
        'rate_limits': {
            'free_tier': {
                'requests_per_minute': 10,
                'requests_per_hour': 50,
                'requests_per_day': 200
            },
            'professional_tier': {
                'requests_per_minute': 100,
                'requests_per_hour': 500,
                'requests_per_day': 2000
            }
        },
        'categories': [
            'Network Issue',
            'Hardware Issue',
            'Software Issue',
            'Account Problem',
            'Payment Issue',
            'Feature Request',
            'Other'
        ],
        'storage': {
            'type': storage_uri.split('://')[0],
            'rate_limiting': 'redis' if storage_uri != 'memory://' else 'in-memory'
        }
    }), 200

@app.route('/api/v1/classify', methods=['POST'])
@require_api_key
@limiter.limit("10 per minute")
def classify():
    """
    Classify a support ticket
    
    Request JSON:
    {
        "ticket": "string (required)",
        "priority": "low|medium|high (optional)"
    }
    """
    start_time = time.time()
    
    # Validate request
    if not request.is_json:
        return jsonify({
            'error': 'Invalid content type',
            'message': 'Content-Type must be application/json',
            'code': 'VAL_001'
        }), 400
    
    data = request.get_json()
    
    # Validate required fields
    if 'ticket' not in data:
        return jsonify({
            'error': 'Missing required field',
            'message': 'Field "ticket" is required',
            'code': 'VAL_002'
        }), 400
    
    ticket_text = data.get('ticket', '').strip()
    
    # Validate ticket content
    if not ticket_text:
        return jsonify({
            'error': 'Invalid ticket content',
            'message': 'Ticket text cannot be empty',
            'code': 'VAL_003'
        }), 400
    
    if len(ticket_text) < 3:
        return jsonify({
            'error': 'Invalid ticket content',
            'message': 'Ticket text must be at least 3 characters',
            'code': 'VAL_004'
        }), 400
    
    # Validate priority if provided
    priority = data.get('priority')
    valid_priorities = ['low', 'medium', 'high']
    
    if priority and priority not in valid_priorities:
        return jsonify({
            'error': 'Invalid priority value',
            'message': f'Priority must be one of: {", ".join(valid_priorities)}',
            'code': 'VAL_005'
        }), 400
    
    try:
        # Classify the ticket
        category, confidence = classify_ticket_mock(ticket_text, priority)
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        # Get rate limit info from headers
        rate_limit_info = {
            'limit': request.headers.get('X-RateLimit-Limit', 'unknown'),
            'remaining': request.headers.get('X-RateLimit-Remaining', 'unknown'),
            'reset': request.headers.get('X-RateLimit-Reset', 'unknown')
        }
        
        response = jsonify({
            'category': category,
            'confidence': confidence,
            'priority': priority or 'medium',
            'processing_time_ms': processing_time,
            'timestamp': datetime.utcnow().isoformat(),
            'api_version': '1.0.0',
            'rate_limits': rate_limit_info
        })
        
        # Add rate limit headers to response
        response.headers['X-RateLimit-Limit'] = '10'
        response.headers['X-RateLimit-Remaining'] = str(max(0, 10 - 1))
        
        return response, 200
        
    except Exception as e:
        app.logger.error(f"Classification error: {str(e)}")
        return jsonify({
            'error': 'Classification failed',
            'message': 'An error occurred during classification',
            'code': 'CLS_001'
        }), 500

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    metrics_data = """# HELP classifications_total Total number of classifications
# TYPE classifications_total counter
classifications_total 0

# HELP classification_duration_seconds Time spent classifying
# TYPE classification_duration_seconds histogram
classification_duration_seconds_bucket{le="0.1"} 0
classification_duration_seconds_bucket{le="0.5"} 0
classification_duration_seconds_bucket{le="1.0"} 0
classification_duration_seconds_bucket{le="+Inf"} 0
classification_duration_seconds_count 0
classification_duration_seconds_sum 0

# HELP api_requests_total Total API requests
# TYPE api_requests_total counter
api_requests_total{endpoint="/api/v1/classify",status="200"} 0

# HELP redis_connection_status Redis connection status
# TYPE redis_connection_status gauge
redis_connection_status{storage="redis"} 1
"""
    return metrics_data, 200, {'Content-Type': 'text/plain; charset=utf-8'}

# ==========================================
# Error Handlers
# ==========================================

@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded"""
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.',
        'code': 'RATE_001',
        'retry_after': e.description
    }), 429

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist',
        'code': 'HTTP_404'
    }), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred',
        'code': 'HTTP_500'
    }), 500

# ==========================================
# Run Application
# ==========================================

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.getenv('FLASK_ENV') == 'development'
    )