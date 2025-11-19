from prometheus_client import Counter, Histogram, Gauge, generate_latest
from flask import Response
import time

# Metrics
request_count = Counter(
    'classifier_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'classifier_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

classification_count = Counter(
    'classifier_predictions_by_category',
    'Predictions by category',
    ['category', 'provider', 'status']
)

error_count = Counter(
    'api_errors_total',
    'Total API errors',
    ['error_type']
)

active_requests = Gauge(
    'api_active_requests',
    'Active requests'
)

def metrics_endpoint():
    """Endpoint для Prometheus"""
    return Response(generate_latest(), mimetype='text/plain')
