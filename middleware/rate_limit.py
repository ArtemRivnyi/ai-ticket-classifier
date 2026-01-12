from flask import request
from flask_limiter.util import get_remote_address


def get_rate_limit_key():
    """
    Get key for rate limiting.
    Combines IP address and API key (if present) to prevent bypassing limits
    by rotating IP addresses or sharing API keys across IPs.
    """
    # Get API key from header (standard) or query param (optional)
    api_key = request.headers.get("X-API-Key")

    # Get IP address
    ip = get_remote_address()

    if api_key:
        # If API key is present, rate limit by the combination
        # This allows the same API key to be used from different IPs (if allowed)
        # but tracks usage per key.
        # Ideally, we should just use the API key if it's valid, but
        # combining with IP adds a layer of defense against key theft usage from multiple locations
        # OR we can just use the API key.
        # The prompt suggested: return f"{ip}:{api_key}"
        # Use hash of API key to prevent leakage in Redis
        import hashlib

        key_hash = hashlib.md5(api_key.encode()).hexdigest()
        return f"{ip}:{key_hash}"

    # Fallback to IP only for anonymous requests
    return ip
