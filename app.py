from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Lazy imports для избежания ошибок
def get_classifier():
    from providers.gemini_provider import GeminiClassifier
    return GeminiClassifier()

@app.route('/api/v1/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0',
        'environment': os.getenv('FLASK_ENV', 'development')
    }), 200

@app.route('/api/v1/classify', methods=['POST'])
def classify():
    """Classification endpoint - simplified for testing"""
    start_time = time.time()
    
    try:
        # Validate API Key
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'X-API-Key header required'}), 401
        
        master_key = os.getenv('MASTER_API_KEY', 'dev_master_key_change_me')
        if api_key != master_key:
            return jsonify({'error': 'Invalid API key'}), 403
        
        # Get ticket
        data = request.get_json()
        if not data or 'ticket' not in data:
            return jsonify({'error': 'ticket field required'}), 400
        
        ticket = data['ticket'].strip()
        if not ticket:
            return jsonify({'error': 'ticket cannot be empty'}), 400
        
        # Classify
        classifier = get_classifier()
        result = classifier.classify(ticket)
        
        duration = time.time() - start_time
        result['processing_time'] = f"{duration:.2f}s"
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/metrics', methods=['GET'])
def metrics():
    """Basic metrics endpoint"""
    return """# HELP api_health API Health Status
# TYPE api_health gauge
api_health 1
""", 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
