import os
import sys
import time
from flask import Flask, g, request
from flask_cors import CORS
from dotenv import load_dotenv

from extensions import db, limiter, cache
from config.settings import get_settings
from config.env_validation import validate_environment
from config.logging_config import setup_logging, logger as structured_logger

# Blueprints
from routes.main import main_bp
from routes.errors import errors_bp
from admin.admin import admin_bp
from api.analytics import analytics_bp
from api.v1.classification import classification_bp

def create_app(test_config=None):
    """Application Factory Pattern"""
    load_dotenv()
    setup_logging()
    logger = structured_logger.bind(component="app_factory")
    
    app = Flask(__name__, static_folder="static", template_folder="templates")
    
    # Settings & Validation
    settings = get_settings()
    env_status = validate_environment(skip_failure="pytest" in sys.modules)
    app.config["ENV_STATUS"] = env_status
    
    # DB Config
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai_ticket_classifier"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize Extensions
    db.init_app(app)
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    limiter.init_app(app)
    
    cache.init_app(app, config={
        "CACHE_TYPE": "RedisCache" if os.getenv("REDIS_URL") else "SimpleCache",
        "CACHE_REDIS_URL": redis_url
    })
    
    # CORS
    CORS(app, origins=settings.cors_origins_list(), supports_credentials=True)
    
    # Provider Initialization (Lazy)
    from providers.multi_provider import MultiProvider
    try:
        classifier = MultiProvider()
        app.config["CLASSIFIER"] = classifier
        logger.info("✅ MultiProvider initialized")
    except Exception as e:
        logger.error(f"❌ Provider init failed: {e}")
        app.config["CLASSIFIER"] = None

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(classification_bp, url_prefix="/api/v1")
    
    # Request Tracing
    from uuid import uuid4
    @app.before_request
    def before_request():
        g.request_id = request.headers.get("X-Request-ID") or f"req_{uuid4().hex}"
        request.start_time = time.time()

    return app
