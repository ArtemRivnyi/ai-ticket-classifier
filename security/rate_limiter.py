from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

def get_api_key():
    """Получаем API key для rate limiting"""
    from flask import request
    return request.headers.get('X-API-Key', get_remote_address())

# Инициализация
limiter = Limiter(
    key_func=get_api_key,
    storage_uri=os.getenv('REDIS_URL', 'redis://redis:6379'),
    default_limits=["1000 per day", "100 per hour"],
    storage_options={"socket_connect_timeout": 30},
    strategy="fixed-window"
)

# Rate limits по tier
TIER_LIMITS = {
    'free': "100 per hour",
    'starter': "1000 per hour", 
    'pro': "10000 per hour",
    'enterprise': "100000 per hour"
}

def tier_rate_limit():
    """Динамический rate limit по tier"""
    from flask import request
    tier = getattr(request, 'user_tier', 'free')
    return TIER_LIMITS.get(tier, TIER_LIMITS['free'])
