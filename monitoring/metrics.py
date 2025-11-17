from prometheus_client import Counter, Histogram, Gauge, generate_latest
from flask import Response
import time

# Metrics
request_count = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'api_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

classification_count = Counter(
    'classifications_total',
    'Total classifications',
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
