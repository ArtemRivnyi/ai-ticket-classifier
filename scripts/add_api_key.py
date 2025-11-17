#!/usr/bin/env python3
"""
Script to manually add an API key to Redis
"""

import os
import sys
import hashlib
from datetime import datetime, timezone

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import APIKeyManager
import redis

def add_manual_key():
    """Add a manual API key to Redis"""
    
    # Your existing key (already a hash)
    existing_key_hash = "093b2dc072107a78d7676dca4cec411fae8e3b2ef80c4dca14a605c116ac1201"
    
    # Connect to Redis
    redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379/0'), decode_responses=True)
    
    key_data = {
        'id': 'manual_admin_key',
        'key_hash': existing_key_hash,
        'user_id': 'admin',
        'name': 'Manual Admin Key', 
        'tier': 'enterprise',
        'is_active': 'true',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'last_used': '',
        'requests_count': '0',
        'rate_limit': '-1'
    }
    
    # Store the key
    redis_client.hset(f"api_key:{existing_key_hash}", mapping=key_data)
    redis_client.sadd(f"user_keys:admin", existing_key_hash)
    
    print(f"✅ API key added successfully!")
    print(f"Key ID: manual_admin_key")
    print(f"User: admin")
    print(f"Tier: enterprise")
    print(f"Use this header: X-API-Key: {existing_key_hash}")

if __name__ == "__main__":
    add_manual_key()