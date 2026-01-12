from prometheus_client import Counter, Histogram, Gauge, generate_latest
from flask import Response
import time

# Existing metrics
request_count = Counter(
    "classifier_requests_total", "Total requests", ["method", "endpoint", "status"]
)

request_duration = Histogram(
    "classifier_request_duration_seconds", "Request duration", ["method", "endpoint"]
)

classification_count = Counter(
    "classifier_predictions_by_category",
    "Predictions by category",
    ["category", "provider", "status"],
)

error_count = Counter("api_errors_total", "Total API errors", ["error_type"])

active_requests = Gauge("api_active_requests", "Active requests")

# NEW: Classification analytics metrics
classification_accuracy = Histogram(
    "classification_confidence_score",
    "Distribution of classification confidence scores",
    buckets=[0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 0.98, 1.0],
)

category_distribution = Counter(
    "category_classifications_total",
    "Distribution of classified categories",
    ["category"],
)

subcategory_distribution = Counter(
    "subcategory_classifications_total",
    "Distribution of classified subcategories",
    ["category", "subcategory"],
)

provider_usage = Counter(
    "provider_usage_total",
    "Classification provider usage",
    ["provider"],  # rule_engine, gemini, openai
)

classification_errors = Counter(
    "classification_errors_total",
    "Classification errors by type",
    ["error_type"],  # validation_error, provider_error, timeout, etc.
)


def metrics_endpoint():
    """Endpoint для Prometheus"""
    return Response(generate_latest(), mimetype="text/plain")
