# app.py - AI Ticket Classifier with Multi-Provider Support
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from classify import classify_ticket
import logging
from logging.handlers import RotatingFileHandler
import os
import traceback
import time
import uuid
import html
from functools import wraps
from pydantic import BaseModel, ValidationError, Field
from typing import List, Optional
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram

# Import Redis modules
from rate_limiter import rate_limit, rate_limiter
from cache_manager import cache_manager

# ===== MULTI-PROVIDER IMPORT =====
try:
    from providers.multi_provider import MultiProviderClassifier
    MULTI_PROVIDER_AVAILABLE = True
except ImportError as e:
    MULTI_PROVIDER_AVAILABLE = False
    print(f"⚠️ Multi-Provider not available: {e}")

app = Flask(__name__)

# ===== CORS Configuration =====
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
CORS(app,
     origins=CORS_ORIGINS,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "X-API-Key", "Authorization"],
     expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"])

# ===== Prometheus Metrics =====
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'AI Ticket Classifier', version='2.0.0')

# Custom metrics
classification_counter = Counter(
    'classifications_total',
    'Total classifications',
    ['category', 'status', 'provider']  # Added 'provider' label
)

classification_duration = Histogram(
    'classification_duration_seconds',
    'Classification duration',
    ['category', 'provider']  # Added 'provider' label
)

api_errors = Counter(
    'api_errors_total',
    'Total API errors',
    ['endpoint', 'error_type']
)

# ===== Logging Configuration =====
if not os.path.exists('logs'):
    os.makedirs('logs')

file_handler = RotatingFileHandler('logs/app.log', maxBytes=10485760, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s'
))
file_handler.setLevel(logging.INFO)

app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# ===== MULTI-PROVIDER INITIALIZATION =====
multi_classifier = None

if MULTI_PROVIDER_AVAILABLE:
    try:
        multi_classifier = MultiProviderClassifier()
        app.logger.info("✅ Multi-Provider system initialized successfully")
        app.logger.info(f"   Available providers: {len(multi_classifier.providers)}")
        for provider in multi_classifier.providers:
            app.logger.info(f"   - {provider.name} (priority: {provider.config.priority})")
    except Exception as e:
        app.logger.error(f"❌ Failed to initialize Multi-Provider: {e}")
        app.logger.error(traceback.format_exc())
        multi_classifier = None
else:
    app.logger.warning("⚠️ Multi-Provider not available - using single provider mode")

# ===== Pydantic Models =====
class ClassifyRequest(BaseModel):
    ticket: str = Field(..., min_length=1, max_length=10000)
    use_multi_provider: Optional[bool] = True  # NEW: Flag to use multi-provider

class BatchClassifyRequest(BaseModel):
    tickets: List[str] = Field(..., min_items=1, max_items=100)
    use_multi_provider: Optional[bool] = True  # NEW

# ===== Middleware =====
@app.before_request
def before_request():
    g.request_id = str(uuid.uuid4())
    g.start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(g, 'request_id'):
        response.headers['X-Request-ID'] = g.request_id
    
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        app.logger.info(f"Request completed")
    
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response

# ===== API Key Authentication =====
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                'error': 'Missing API key',
                'code': 401,
                'details': 'Provide X-API-Key header',
                'request_id': getattr(g, 'request_id', None)
            }), 401
        
        # TODO: Add actual API key validation from database
        valid_key = os.getenv('API_KEY', '093b2dc072107a78d7676dca4cec411fae8e3b2ef80c4dca14a605c116ac1201')
        
        if api_key != valid_key:
            api_errors.labels(endpoint=request.endpoint, error_type='invalid_api_key').inc()
            return jsonify({
                'error': 'Invalid API key',
                'code': 403,
                'request_id': getattr(g, 'request_id', None)
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

# ===== Helper Functions =====
def sanitize_input(text: str) -> str:
    """Sanitize input text"""
    return html.escape(text.strip())

def classify_with_fallback(ticket_text: str) -> dict:
    """
    Classify ticket with multi-provider fallback
    Falls back to single provider if multi-provider fails
    """
    
    # Try multi-provider first (if available and enabled)
    if multi_classifier:
        try:
            app.logger.info("🔄 Using Multi-Provider classification")
            result = multi_classifier.classify(ticket_text)
            
            # Add standard fields if missing
            if 'request_id' not in result:
                result['request_id'] = getattr(g, 'request_id', None)
            if 'cached' not in result:
                result['cached'] = False
            
            app.logger.info(f"✅ Multi-Provider success: {result.get('provider')}")
            return result
            
        except Exception as e:
            app.logger.error(f"❌ Multi-Provider failed: {e}")
            app.logger.warning("↪️ Falling back to single provider")
    
    # Fallback to original classify_ticket function
    app.logger.info("📋 Using single provider classification")
    
    try:
        category, confidence = classify_ticket(ticket_text)
        
        return {
            'category': category,
            'confidence': confidence,
            'provider': 'gemini_single',
            'processing_time_ms': 0,
            'cached': False,
            'request_id': getattr(g, 'request_id', None)
        }
    except Exception as e:
        app.logger.error(f"❌ Single provider also failed: {e}")
        raise

# ===== API Endpoints =====

@app.route('/api/v1/health', methods=['GET'])
def health():
    """Health check endpoint"""
    app.logger.info("Health check called")
    
    # Check multi-provider health
    mp_status = "not_available"
    if multi_classifier:
        try:
            health_status = multi_classifier.get_health_status()
            available_providers = sum(1 for p in health_status['providers'] if p['available'])
            mp_status = f"{available_providers}/{len(health_status['providers'])} providers available"
        except:
            mp_status = "error"
    
    return jsonify({
        'status': 'ok',
        'version': '2.0.0',
        'multi_provider': mp_status,
        'cache': 'enabled' if cache_manager else 'disabled',
        'rate_limiter': 'enabled' if rate_limiter else 'disabled'
    }), 200

@app.route('/api/v1/info', methods=['GET'])
def info():
    """API information"""
    endpoints = {
        'health': '/api/v1/health',
        'classify': '/api/v1/classify',
        'batch_classify': '/api/v1/batch_classify',
        'cache_stats': '/api/v1/cache/stats',
        'openapi': '/api/v1/openapi.json'
    }
    
    # Add multi-provider endpoints if available
    if multi_classifier:
        endpoints.update({
            'providers_health': '/api/v1/providers/health',
            'providers_stats': '/api/v1/providers/stats'
        })
    
    return jsonify({
        'name': 'AI Ticket Classifier',
        'version': '2.0.0',
        'features': {
            'multi_provider': MULTI_PROVIDER_AVAILABLE and multi_classifier is not None,
            'caching': cache_manager is not None,
            'rate_limiting': rate_limiter is not None,
            'metrics': True,
            'batch_processing': True
        },
        'endpoints': endpoints
    }), 200

@app.route('/api/v1/classify', methods=['POST'])
@require_api_key
@rate_limit(limit=50, window=60)
def classify():
    """
    Single ticket classification with multi-provider support
    
    Request body:
    {
        "ticket": "My laptop is broken",
        "use_multi_provider": true  // optional, default: true
    }
    """
    start_time = time.time()
    
    try:
        # Validate request
        data = ClassifyRequest(**request.json)
        ticket_text = sanitize_input(data.ticket)
        
        app.logger.info(f"Classification request: {ticket_text[:100]}")
        
        # Check cache first
        cache_key = f"cache:ticket:{ticket_text[:100]}"
        cached_result = cache_manager.get(cache_key)
        
        if cached_result:
            app.logger.info(f"Cache HIT for key: {cache_key[:50]}")
            cached_result['cached'] = True
            cached_result['request_id'] = g.request_id
            
            classification_counter.labels(
                category=cached_result.get('category', 'unknown'),
                status='success',
                provider='cache'
            ).inc()
            
            return jsonify(cached_result), 200
        
        app.logger.info(f"Cache MISS for key: {cache_key[:50]}")
        
        # Classify with fallback
        result = classify_with_fallback(ticket_text)
        
        # Add metadata
        processing_time = (time.time() - start_time) * 1000
        result['processing_time_ms'] = round(processing_time, 2)
        result['request_id'] = g.request_id
        result['cached'] = False
        
        # Cache result
        cache_manager.set(cache_key, result, ttl=3600)
        app.logger.info(f"Cached result for key: {cache_key[:50]} (TTL: 3600s)")
        
        # Update metrics
        provider = result.get('provider', 'unknown')
        category = result.get('category', 'unknown')
        
        classification_counter.labels(
            category=category,
            status='success',
            provider=provider
        ).inc()
        
        classification_duration.labels(
            category=category,
            provider=provider
        ).observe(processing_time / 1000)
        
        app.logger.info(f"Classified ticket as: {category} (provider: {provider})")
        
        return jsonify(result), 200
        
    except ValidationError as e:
        api_errors.labels(endpoint='classify', error_type='validation_error').inc()
        return jsonify({
            'error': 'Validation error',
            'details': e.errors(),
            'request_id': g.request_id
        }), 400
    
    except Exception as e:
        api_errors.labels(endpoint='classify', error_type='internal_error').inc()
        app.logger.error(f"Classification error: {e}")
        app.logger.error(traceback.format_exc())
        
        return jsonify({
            'error': 'Classification failed',
            'message': str(e),
            'request_id': g.request_id
        }), 500

@app.route('/api/v1/batch_classify', methods=['POST'])
@require_api_key
@rate_limit(limit=10, window=60)
def batch_classify():
    """
    Batch classification with multi-provider support
    
    Request body:
    {
        "tickets": ["ticket1", "ticket2", ...],
        "use_multi_provider": true  // optional
    }
    """
    try:
        data = BatchClassifyRequest(**request.json)
        tickets = [sanitize_input(t) for t in data.tickets]
        
        app.logger.info(f"Batch classification: {len(tickets)} tickets")
        
        results = []
        errors = []
        
        for idx, ticket in enumerate(tickets):
            try:
                result = classify_with_fallback(ticket)
                results.append(result)
                
                provider = result.get('provider', 'unknown')
                category = result.get('category', 'unknown')
                
                classification_counter.labels(
                    category=category,
                    status='success',
                    provider=provider
                ).inc()
                
            except Exception as e:
                errors.append({
                    'index': idx,
                    'ticket': ticket[:100],
                    'error': str(e)
                })
                
                classification_counter.labels(
                    category='unknown',
                    status='error',
                    provider='unknown'
                ).inc()
        
        return jsonify({
            'total': len(tickets),
            'successful': len(results),
            'failed': len(errors),
            'results': results,
            'errors': errors if errors else None,
            'request_id': g.request_id
        }), 200
        
    except ValidationError as e:
        api_errors.labels(endpoint='batch_classify', error_type='validation_error').inc()
        return jsonify({
            'error': 'Validation error',
            'details': e.errors(),
            'request_id': g.request_id
        }), 400
    
    except Exception as e:
        api_errors.labels(endpoint='batch_classify', error_type='internal_error').inc()
        app.logger.error(f"Batch classification error: {e}")
        
        return jsonify({
            'error': 'Batch classification failed',
            'message': str(e),
            'request_id': g.request_id
        }), 500

# ===== MULTI-PROVIDER SPECIFIC ENDPOINTS =====

@app.route('/api/v1/providers/health', methods=['GET'])
def providers_health():
    """
    Get health status of all AI providers
    
    Returns circuit breaker states, availability, etc.
    """
    if not multi_classifier:
        return jsonify({
            'error': 'Multi-provider not available',
            'mode': 'single_provider',
            'message': 'Multi-provider system is not initialized'
        }), 200
    
    try:
        health_status = multi_classifier.get_health_status()
        return jsonify(health_status), 200
    
    except Exception as e:
        app.logger.error(f"Error getting provider health: {e}")
        return jsonify({
            'error': 'Failed to get provider health',
            'message': str(e)
        }), 500

@app.route('/api/v1/providers/stats', methods=['GET'])
def providers_stats():
    """
    Get usage statistics for all providers
    
    Returns request counts, success rates, etc.
    """
    if not multi_classifier:
        return jsonify({
            'error': 'Multi-provider not available',
            'mode': 'single_provider'
        }), 200
    
    try:
        stats = multi_classifier.get_stats()
        return jsonify(stats), 200
    
    except Exception as e:
        app.logger.error(f"Error getting provider stats: {e}")
        return jsonify({
            'error': 'Failed to get provider stats',
            'message': str(e)
        }), 500

# ===== CACHE ENDPOINTS =====

@app.route('/api/v1/cache/stats', methods=['GET'])
def cache_stats():
    """Cache statistics"""
    if not cache_manager:
        return jsonify({'error': 'Cache not available'}), 503
    
    try:
        stats = cache_manager.get_stats()
        return jsonify({
            'enabled': True,
            'stats': stats
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/cache/clear', methods=['POST'])
@require_api_key
def clear_cache():
    """Clear cache"""
    if not cache_manager:
        return jsonify({'error': 'Cache not available'}), 503
    
    try:
        cache_manager.clear()
        return jsonify({'message': 'Cache cleared successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== OPENAPI DOCUMENTATION =====

@app.route('/api/v1/openapi.json', methods=['GET'])
def openapi_spec():
    """OpenAPI 3.0 specification"""
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "AI Ticket Classifier API",
            "version": "2.0.0",
            "description": "Production-ready AI ticket classification with multi-provider fallback"
        },
        "servers": [
            {"url": "http://localhost:5000", "description": "Local development"},
            {"url": "https://api.your-domain.com", "description": "Production"}
        ],
        "paths": {
            "/api/v1/classify": {
                "post": {
                    "summary": "Classify a single ticket",
                    "security": [{"ApiKeyAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["ticket"],
                                    "properties": {
                                        "ticket": {"type": "string", "example": "My laptop is broken"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Classification successful"},
                        "401": {"description": "Missing or invalid API key"},
                        "429": {"description": "Rate limit exceeded"}
                    }
                }
            },
            "/api/v1/batch_classify": {
                "post": {
                    "summary": "Classify multiple tickets",
                    "security": [{"ApiKeyAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["tickets"],
                                    "properties": {
                                        "tickets": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/providers/health": {
                "get": {
                    "summary": "Check health of all AI providers",
                    "responses": {
                        "200": {"description": "Provider health status"}
                    }
                }
            }
        },
        "components": {
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key"
                }
            }
        }
    }
    
    return jsonify(spec), 200

# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist',
        'request_id': getattr(g, 'request_id', None)
    }), 404

@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': str(e),
        'request_id': getattr(g, 'request_id', None)
    }), 429

@app.errorhandler(500)
def internal_error(e):
    app.logger.error(f"Internal error: {e}")
    app.logger.error(traceback.format_exc())
    
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred',
        'request_id': getattr(g, 'request_id', None)
    }), 500

# ===== STARTUP =====

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 AI Ticket Classifier API v2.0.0")
    print("=" * 60)
    print(f"Multi-Provider: {'✅ Enabled' if multi_classifier else '❌ Disabled'}")
    print(f"Caching: {'✅ Enabled' if cache_manager else '❌ Disabled'}")
    print(f"Rate Limiting: {'✅ Enabled' if rate_limiter else '❌ Disabled'}")
    print("=" * 60)
    
    if multi_classifier:
        print("\n📊 Available Providers:")
        for p in multi_classifier.providers:
            status = "🟢" if p.is_available() else "🔴"
            print(f"  {status} {p.name} (priority: {p.config.priority})")
    
    print("\n🌐 Server starting on http://0.0.0.0:5000")
    print("📖 API Docs: http://localhost:5000/api/v1/openapi.json")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)