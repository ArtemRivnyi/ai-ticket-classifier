#!/usr/bin/env python3
"""
Test script for API authentication system
"""

import os
import sys
import requests
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_api_endpoints():
    """Test API endpoints with different authentication scenarios"""
    
    base_url = "http://localhost:5000"
    test_key = "093b2dc072107a78d7676dca4cec411fae8e3b2ef80c4dca14a605c116ac1201"
    
    print("🧪 Testing API Authentication System...")
    
    # Test 1: Request without API key
    print("\n1. Testing without API key...")
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly rejected unauthorized request")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Request with invalid API key
    print("\n2. Testing with invalid API key...")
    try:
        headers = {'X-API-Key': 'invalid_key_123'}
        response = requests.get(f"{base_url}/api/health", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly rejected invalid key")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Request with valid API key
    print("\n3. Testing with valid API key...")
    try:
        headers = {'X-API-Key': test_key}
        response = requests.get(f"{base_url}/api/health", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Successfully authenticated")
        else:
            print(f"   ❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Test rate limiting
    print("\n4. Testing rate limiting...")
    try:
        headers = {'X-API-Key': test_key}
        for i in range(5):
            response = requests.get(f"{base_url}/api/health", headers=headers)
            remaining = response.headers.get('X-RateLimit-Remaining', 'N/A')
            print(f"   Request {i+1}: Status {response.status_code}, Remaining: {remaining}")
            time.sleep(0.1)
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_redis_connection():
    """Test Redis connection"""
    print("\n🔍 Testing Redis connection...")
    try:
        from auth import redis_client
        if redis_client and redis_client.ping():
            print("   ✅ Redis connection successful")
            
            # Test key storage
            test_data = redis_client.hgetall("api_key:093b2dc072107a78d7676dca4cec411fae8e3b2ef80c4dca14a605c116ac1201")
            if test_data:
                print("   ✅ API key found in Redis")
                print(f"   Key data: {test_data}")
            else:
                print("   ❌ API key not found in Redis")
        else:
            print("   ❌ Redis connection failed")
    except Exception as e:
        print(f"   ❌ Redis error: {e}")

if __name__ == "__main__":
    test_redis_connection()
    test_api_endpoints()