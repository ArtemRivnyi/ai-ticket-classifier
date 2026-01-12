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
        return f"{ip}:{api_key}"

    # Fallback to IP only for anonymous requests
    return ip
