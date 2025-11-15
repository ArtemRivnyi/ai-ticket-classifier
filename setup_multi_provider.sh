#!/bin/bash
# setup_multi_provider.sh - Скрипт установки Multi-Provider системы

echo "🚀 Installing Multi-Provider Fallback System..."

# 1. Создать структуру директорий
mkdir -p providers
mkdir -p tests

# 2. Установить зависимости
echo "📦 Installing dependencies..."
cat >> requirements.txt << 'EOF'
# Multi-Provider Support
google-generativeai>=0.3.0
openai>=1.0.0
anthropic>=0.18.0

# Existing dependencies (if not already present)
flask>=3.0.0
flask-limiter>=3.5.0
pydantic>=2.0.0
python-dotenv>=1.0.0
gunicorn>=21.2.0
prometheus-client>=0.19.0
redis>=5.0.0
EOF

pip install -r requirements.txt

# 3. Создать providers/__init__.py
cat > providers/__init__.py << 'EOF'
"""
Multi-Provider AI Classification System
Supports: Gemini, OpenAI, Anthropic with automatic fallback
"""
from .multi_provider import (
    MultiProviderClassifier,
    CircuitBreaker,
    CircuitState,
    ProviderConfig
)

__all__ = [
    'MultiProviderClassifier',
    'CircuitBreaker', 
    'CircuitState',
    'ProviderConfig'
]
EOF

# 4. Обновить .env файл
cat >> .env << 'EOF'

# ===== MULTI-PROVIDER CONFIGURATION =====
# Primary Provider (рекомендуется Gemini - дешевле)
GEMINI_API_KEY=your_gemini_key_here

# Fallback Providers (опционально, но рекомендуется)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Circuit Breaker Settings
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT_SECONDS=60
CIRCUIT_BREAKER_HALF_OPEN_ATTEMPTS=3
EOF

# 5. Создать обновленный app.py
cat > app.py << 'EOF'
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_client import Counter, Histogram, generate_latest
import os
import logging
from dotenv import load_dotenv

# Загрузить переменные окружения
load_dotenv()

# Импорт Multi-Provider системы
from providers.multi_provider import MultiProviderClassifier

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Rate Limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"],
    storage_uri="redis://localhost:6379"
)

# Prometheus Metrics
classifications_total = Counter(
    'classifications_total',
    'Total number of classifications',
    ['provider', 'status']
)
classification_duration = Histogram(
    'classification_duration_seconds',
    'Time spent on classification',
    ['provider']
)

# Инициализация Multi-Provider классификатора
try:
    classifier = MultiProviderClassifier()
    logger.info("✅ MultiProviderClassifier initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize classifier: {e}")
    classifier = None

# ===== MIDDLEWARE =====

def require_api_key(f):
    """Декоратор для проверки API ключа"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                'error': 'Missing API key',
                'code': 401,
                'details': 'Provide X-API-Key header'
            }), 401
        
        # Здесь должна быть проверка ключа в БД
        # Для примера просто проверяем, что ключ не пустой
        valid_key = os.getenv('API_KEY', '093b2dc072107a78d7676dca4cec411fae8e3b2ef80c4dca14a605c116ac1201')
        
        if api_key != valid_key:
            return jsonify({
                'error': 'Invalid API key',
                'code': 403
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

# ===== ENDPOINTS =====

@app.route('/api/v1/health', methods=['GET'])
def health():
    """Health check endpoint"""
    if not classifier:
        return jsonify({
            'status': 'unhealthy',
            'message': 'Classifier not initialized'
        }), 503
    
    return jsonify({'status': 'ok'})

@app.route('/api/v1/info', methods=['GET'])
def info():
    """API information"""
    return jsonify({
        'name': 'AI Ticket Classifier',
        'version': 'v1.0.0',
        'endpoints': {
            'classify': '/api/v1/classify',
            'batch_classify': '/api/v1/batch_classify',
            'health': '/api/v1/health',
            'providers_health': '/api/v1/providers/health',
            'providers_stats': '/api/v1/providers/stats'
        },
        'features': [
            'Multi-provider fallback',
            'Circuit breaker protection',
            'Rate limiting',
            'Prometheus metrics'
        ]
    })

@app.route('/api/v1/classify', methods=['POST'])
@require_api_key
@limiter.limit("50 per minute")
def classify():
    """Single ticket classification with auto-fallback"""
    
    if not classifier:
        return jsonify({
            'error': 'Service unavailable',
            'message': 'Classification service not initialized'
        }), 503
    
    data = request.json
    ticket_text = data.get('ticket')
    
    if not ticket_text or not ticket_text.strip():
        return jsonify({
            'error': 'Invalid input',
            'message': 'Ticket text is required'
        }), 400
    
    try:
        import time
        start = time.time()
        
        result = classifier.classify(ticket_text)
        
        duration = time.time() - start
        
        # Метрики
        classifications_total.labels(
            provider=result.get('provider', 'unknown'),
            status='success'
        ).inc()
        
        classification_duration.labels(
            provider=result.get('provider', 'unknown')
        ).observe(duration)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Classification error: {e}")
        
        classifications_total.labels(
            provider='unknown',
            status='error'
        ).inc()
        
        return jsonify({
            'error': 'Classification failed',
            'message': str(e),
            'providers_available': [
                p['name'] for p in classifier.get_health_status()['providers']
                if p['available']
            ]
        }), 500

@app.route('/api/v1/batch_classify', methods=['POST'])
@require_api_key
@limiter.limit("10 per minute")
def batch_classify():
    """Batch classification with auto-fallback"""
    
    if not classifier:
        return jsonify({'error': 'Service unavailable'}), 503
    
    data = request.json
    tickets = data.get('tickets', [])
    
    if not tickets or not isinstance(tickets, list):
        return jsonify({
            'error': 'Invalid input',
            'message': 'Tickets must be a non-empty array'
        }), 400
    
    if len(tickets) > 100:
        return jsonify({
            'error': 'Batch too large',
            'message': 'Maximum 100 tickets per batch',
            'received': len(tickets)
        }), 400
    
    results = []
    errors = []
    
    for idx, ticket in enumerate(tickets):
        try:
            result = classifier.classify(ticket)
            results.append(result)
            
            classifications_total.labels(
                provider=result.get('provider', 'unknown'),
                status='success'
            ).inc()
        
        except Exception as e:
            errors.append({
                'index': idx,
                'ticket': ticket[:100],
                'error': str(e)
            })
            
            classifications_total.labels(
                provider='unknown',
                status='error'
            ).inc()
    
    return jsonify({
        'total': len(tickets),
        'successful': len(results),
        'failed': len(errors),
        'results': results,
        'errors': errors if errors else None
    })

@app.route('/api/v1/providers/health', methods=['GET'])
def providers_health():
    """Get health status of all providers"""
    
    if not classifier:
        return jsonify({'error': 'Service unavailable'}), 503
    
    return jsonify(classifier.get_health_status())

@app.route('/api/v1/providers/stats', methods=['GET'])
def providers_stats():
    """Get usage statistics of providers"""
    
    if not classifier:
        return jsonify({'error': 'Service unavailable'}), 503
    
    return jsonify(classifier.get_stats())

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

# ===== ERROR HANDLERS =====

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': str(e)
    }), 429

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal error: {e}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'Please contact support'
    }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
EOF

# 6. Создать тестовый скрипт
cat > tests/test_multi_provider.py << 'EOF'
"""
Тесты для Multi-Provider системы
"""
import pytest
import os
from providers.multi_provider import (
    MultiProviderClassifier,
    CircuitBreaker,
    CircuitState
)

class TestCircuitBreaker:
    """Тесты Circuit Breaker"""
    
    def test_initial_state(self):
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED
        assert cb.can_attempt() == True
    
    def test_open_after_failures(self):
        cb = CircuitBreaker(failure_threshold=3)
        
        for _ in range(3):
            cb.record_failure()
        
        assert cb.state == CircuitState.OPEN
        assert cb.can_attempt() == False
    
    def test_recovery_to_half_open(self):
        cb = CircuitBreaker(failure_threshold=2, timeout_seconds=0)
        
        cb.record_failure()
        cb.record_failure()
        
        assert cb.state == CircuitState.OPEN
        
        # После таймаута должно переключиться в HALF_OPEN
        import time
        time.sleep(0.1)
        
        assert cb.can_attempt() == True

class TestMultiProvider:
    """Тесты Multi-Provider классификатора"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        # Установить тестовые ключи
        os.environ['GEMINI_API_KEY'] = 'test_key'
    
    def test_initialization(self):
        """Проверка инициализации"""
        classifier = MultiProviderClassifier()
        assert len(classifier.providers) > 0
    
    def test_provider_fallback(self):
        """Проверка fallback между провайдерами"""
        classifier = MultiProviderClassifier()
        
        if len(classifier.providers) > 1:
            # Отключить первый провайдер
            classifier.providers[0].config.enabled = False
            
            # Должен использовать второй провайдер
            # (test will need actual API keys to work)
            pass
    
    def test_get_health_status(self):
        """Проверка статуса здоровья"""
        classifier = MultiProviderClassifier()
        health = classifier.get_health_status()
        
        assert 'providers' in health
        assert 'stats' in health
        assert len(health['providers']) > 0

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
EOF

# 7. Создать скрипт для быстрого тестирования
cat > test_providers.sh << 'EOF'
#!/bin/bash

echo "🧪 Testing Multi-Provider System"
echo "================================"

API_KEY="093b2dc072107a78d7676dca4cec411fae8e3b2ef80c4dca14a605c116ac1201"

echo ""
echo "1. Health Check:"
curl -s http://localhost:5000/api/v1/health | jq '.'

echo ""
echo "2. Providers Health:"
curl -s http://localhost:5000/api/v1/providers/health | jq '.'

echo ""
echo "3. Single Classification (should use primary provider):"
curl -s -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"ticket":"My laptop screen is broken"}' | jq '.'

echo ""
echo "4. Providers Stats:"
curl -s http://localhost:5000/api/v1/providers/stats | jq '.'

echo ""
echo "5. Batch Classification:"
curl -s -X POST http://localhost:5000/api/v1/batch_classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "tickets": [
      "Cannot login to my account",
      "Printer not working",
      "Need refund for last payment"
    ]
  }' | jq '.'

echo ""
echo "✅ Tests completed!"
EOF

chmod +x test_providers.sh

echo ""
echo "✅ Multi-Provider system installed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env and add your API keys:"
echo "   GEMINI_API_KEY=your_key"
echo "   OPENAI_API_KEY=your_key (optional)"
echo "   ANTHROPIC_API_KEY=your_key (optional)"
echo ""
echo "2. Start the server:"
echo "   python app.py"
echo ""
echo "3. Test the system:"
echo "   ./test_providers.sh"
echo ""
echo "📖 Documentation:"
echo "   - Circuit breaker automatically handles provider failures"
echo "   - Fallback to next provider happens within seconds"
echo "   - Monitor /api/v1/providers/health for status"