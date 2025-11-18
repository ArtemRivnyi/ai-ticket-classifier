#!/usr/bin/env python3
"""
Generate test data for Prometheus and Grafana dashboards
This script sends multiple classification requests to populate metrics
"""

import requests
import time
import json
import sys
import os
from typing import Optional

BASE_URL = "http://localhost:5000"

# Test tickets for different categories
TEST_TICKETS = [
    # Network Issues
    "I cannot connect to the internet. WiFi shows connected but no websites load.",
    "Network connection is very slow today. Pages take forever to load.",
    "My internet keeps disconnecting every few minutes.",
    "Cannot access company VPN. Connection times out.",
    "WiFi password not working after router reset.",
    
    # Account Problems
    "I forgot my password and cannot log into my account.",
    "My account is locked after multiple failed login attempts.",
    "Cannot reset password - email not received.",
    "Account shows wrong email address. Need to update it.",
    "Two-factor authentication not working.",
    
    # Payment Issues
    "My credit card was charged twice for the subscription.",
    "Payment failed with error code 500. Card is valid.",
    "Need refund for cancelled subscription.",
    "Invoice shows incorrect amount. Please correct it.",
    "Payment method expired. Cannot update it.",
    
    # Feature Requests
    "Please add dark mode to the application.",
    "It would be great if you could add export to PDF feature.",
    "Can you add support for mobile app?",
    "Request for bulk import functionality.",
    "Please add keyboard shortcuts for common actions.",
    
    # Other
    "General question about service hours.",
    "What are your business hours?",
    "How do I contact customer support?",
    "Where can I find the user manual?",
    "General inquiry about pricing plans."
]


def register_api_key(email: str = None, name: str = None, organization: str = None) -> Optional[str]:
    """Register a new API key"""
    import random
    import string
    
    # Generate unique values if not provided
    if not email:
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        email = f"test_{random_str}@example.com"
    if not name:
        name = f"Test User {random_str[:4]}"
    if not organization:
        organization = f"Test Org {random_str[:4]}"
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={
                "email": email,
                "name": name,
                "organization": organization
            },
            headers={
                "Content-Type": "application/json",
                "X-Forwarded-Proto": "https"
            },
            timeout=10
        )
        if response.status_code == 201:
            data = response.json()
            api_key = data.get("api_key")
            if api_key:
                print(f"[OK] Registered API key: {api_key[:20]}...")
                return api_key
            else:
                print(f"[WARN] Registration successful but no API key returned")
                return None
        elif response.status_code == 400:
            # Try with different email
            random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            email = f"test_{random_str}@example.com"
            name = f"Test User {random_str[:4]}"
            organization = f"Test Org {random_str[:4]}"
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/register",
                json={
                    "email": email,
                    "name": name,
                    "organization": organization
                },
                headers={
                    "Content-Type": "application/json",
                    "X-Forwarded-Proto": "https"
                },
                timeout=10
            )
            if response.status_code == 201:
                data = response.json()
                api_key = data.get("api_key")
                if api_key:
                    print(f"[OK] Registered API key: {api_key[:20]}...")
                    return api_key
        response.raise_for_status()
        return None
    except Exception as e:
        print(f"[ERROR] Failed to register API key: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"[ERROR] Details: {error_data}")
            except:
                print(f"[ERROR] Response: {e.response.text}")
        print(f"[INFO] You can use existing API key by setting API_KEY environment variable")
        return None


def classify_ticket(api_key: str, ticket: str) -> bool:
    """Classify a single ticket"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/classify",
            json={"ticket": ticket},
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key,
                "X-Forwarded-Proto": "https"
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        category = data.get("category", "Unknown")
        provider = data.get("provider", "Unknown")
        print(f"  [OK] {category[:30]:<30} [{provider}]")
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def batch_classify(api_key: str, tickets: list, batch_size: int = 5) -> int:
    """Classify multiple tickets in batches"""
    success_count = 0
    for i in range(0, len(tickets), batch_size):
        batch = tickets[i:i + batch_size]
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/batch",
                json={"tickets": batch},
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": api_key,
                    "X-Forwarded-Proto": "https"
                },
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            success_count += len([r for r in results if r.get("status") == "success"])
            print(f"  [OK] Batch {i//batch_size + 1}: {len(results)} tickets classified")
        except Exception as e:
            print(f"  [ERROR] Batch error: {e}")
        time.sleep(0.5)  # Small delay between batches
    return success_count


def check_health() -> bool:
    """Check if API is healthy"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/health",
            headers={"X-Forwarded-Proto": "https"},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        print(f"[OK] API Status: {data.get('status', 'unknown')}")
        print(f"   Gemini: {data.get('provider_status', {}).get('gemini', 'unknown')}")
        return True
    except Exception as e:
        print(f"[ERROR] Health check failed: {e}")
        return False


def main():
    """Main function to generate test data"""
    print("=" * 70)
    print("Test Data Generator for Prometheus & Grafana")
    print("=" * 70)
    print()
    
    # Check health
    if not check_health():
        print("\n[ERROR] API is not available. Make sure Docker containers are running:")
        print("   docker-compose up -d")
        sys.exit(1)
    
    print()
    
    # Register API key
    api_key = os.environ.get("API_KEY")
    if not api_key:
        print("[*] Registering API key...")
        api_key = register_api_key()
        if not api_key:
            print("\n[ERROR] Failed to register API key.")
            print("[INFO] You can set API_KEY environment variable to use existing key")
            sys.exit(1)
    else:
        print(f"[OK] Using API key from environment: {api_key[:20]}...")
    
    print()
    print("[*] Starting classification requests...")
    print("-" * 70)
    
    # Single classifications
    print("\n[1] Single Classifications:")
    single_count = 0
    for i, ticket in enumerate(TEST_TICKETS[:10], 1):
        print(f"  [{i:2d}] ", end="")
        if classify_ticket(api_key, ticket):
            single_count += 1
        time.sleep(0.3)  # Small delay to avoid rate limiting
    
    print(f"\n   [OK] {single_count}/{min(10, len(TEST_TICKETS))} successful")
    
    # Batch classifications
    print("\n[2] Batch Classifications:")
    batch_tickets = TEST_TICKETS[10:]
    batch_count = batch_classify(api_key, batch_tickets, batch_size=5)
    print(f"   [OK] {batch_count} tickets classified in batches")
    
    # Summary
    total = single_count + batch_count
    print()
    print("=" * 70)
    print(f"[OK] Generated {total} classification requests")
    print("=" * 70)
    print()
    print("View metrics:")
    print("  - Prometheus: http://localhost:9090")
    print("  - Grafana:    http://localhost:3000")
    print()
    print("Tip: Wait a few seconds for metrics to update, then refresh Grafana dashboard")
    print()


if __name__ == "__main__":
    main()

