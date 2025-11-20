import requests
import json
import os
import random
import string

API_URL = "http://localhost:5000"

def register_api_key():
    """Register a new API key"""
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    try:
        response = requests.post(
            f"{API_URL}/api/v1/auth/register",
            json={
                "email": f"test_{random_str}@example.com",
                "name": f"Test User {random_str[:4]}",
                "organization": f"Test Org {random_str[:4]}"
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
                print(f"✅ Registered API key: {api_key[:20]}...")
                return api_key
    except Exception as e:
        print(f"❌ Failed to register API key: {e}")
    return None

# Test cases from the checklist
TEST_CASES = [
    # 2.1 Login issues → Should be Authentication Issue (NOT Bug)
    {
        "ticket": "I cannot log in. The verification code is invalid.",
        "expected": "Authentication Issue",
        "reason": "Login with invalid 2FA code"
    },
    {
        "ticket": "Reset link expired before I could use it.",
        "expected": "Authentication Issue",
        "reason": "Password reset link expired"
    },
    {
        "ticket": "2FA verification failed. Cannot access my account.",
        "expected": "Authentication Issue",
        "reason": "2FA failure"
    },
    
    # 2.2 Money charged → Should be Payment Issue (NOT Bug)
    {
        "ticket": "I was charged twice for the same subscription.",
        "expected": "Payment Issue",
        "reason": "Duplicate charge"
    },
    {
        "ticket": "Payment completed but I want a refund.",
        "expected": "Payment Issue",
        "reason": "Refund request"
    },
    {
        "ticket": "Unauthorized payment of $500 appeared on my card.",
        "expected": "Payment Issue",
        "reason": "Unauthorized charge"
    },
    
    # 2.3 Hardware devices → Should be Hardware Issue (NOT Network Issue)
    {
        "ticket": "Camera stopped working after firmware update.",
        "expected": "Hardware Issue",
        "reason": "Camera malfunction"
    },
    {
        "ticket": "Sensor battery drains in one hour.",
        "expected": "Hardware Issue",
        "reason": "Sensor battery issue"
    },
    {
        "ticket": "Printer keeps jamming. Already cleaned it twice.",
        "expected": "Hardware Issue",
        "reason": "Printer hardware problem"
    },
    {
        "ticket": "Card reader not detecting cards anymore.",
        "expected": "Hardware Issue",
        "reason": "Card reader malfunction"
    },
    
    # 2.4 Integration issues → Should be Integration Issue
    {
        "ticket": "Slack integration only sends alerts to half of our team.",
        "expected": "Integration Issue",
        "reason": "Partial Slack delivery"
    },
    {
        "ticket": "Webhook callbacks timing out. API not responding.",
        "expected": "Integration Issue",
        "reason": "Webhook timeout"
    },
    {
        "ticket": "SSO login with Azure AD failing. Error: invalid_grant.",
        "expected": "Integration Issue",
        "reason": "SSO failure"
    },
    
    # 2.5 UI/Backend mismatch → Should be Billing Bug (NOT Other)
    {
        "ticket": "UI shows paid but Stripe webhook shows failed.",
        "expected": "Billing Bug",
        "reason": "UI/backend payment mismatch"
    },
    {
        "ticket": "Invoice says $100 but processor charged $150.",
        "expected": "Billing Bug",
        "reason": "Invoice/processor mismatch"
    },
    {
        "ticket": "Dashboard shows paid subscription but backend logs show unpaid.",
        "expected": "Billing Bug",
        "reason": "Dashboard/backend mismatch"
    },
    
    # Notification issues
    {
        "ticket": "Email notifications not delivered to some users.",
        "expected": "Notification Issue",
        "reason": "Partial email delivery"
    },
    {
        "ticket": "Half of the team gets Slack alerts, the other half doesn't.",
        "expected": "Notification Issue",
        "reason": "Partial notification delivery"
    },
    
    # Mixed issues
    {
        "ticket": "Cannot log in AND my payment failed. Two separate issues.",
        "expected": "Mixed Issue",
        "reason": "Multiple problems in one ticket"
    },
    
    # Low priority
    {
        "ticket": "Minor cosmetic issue with button alignment. Not urgent.",
        "expected": "Bug/Technical Issue",
        "expected_priority": "low",
        "reason": "Low priority cosmetic bug"
    },
    {
        "ticket": "Nice to have: add animation to the loading screen.",
        "expected": "Feature Request",
        "expected_priority": "low",
        "reason": "Low priority feature request"
    },
]


def classify_ticket(ticket_text, api_key):
    """Classify a ticket using the API"""
    try:
        response = requests.post(
            f"{API_URL}/api/v1/classify",
            json={"ticket": ticket_text},
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key,
                "X-Forwarded-Proto": "https"
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def main():
    print("=" * 80)
    print("CLASSIFIER ACCURACY TEST - Edge Cases from Checklist")
    print("=" * 80)
    print()
    
    # Register API key
    api_key = register_api_key()
    if not api_key:
        print("❌ Failed to register API key. Exiting.")
        return
    
    print()
    
    correct = 0
    total = len(TEST_CASES)
    errors = []
    
    for i, test_case in enumerate(TEST_CASES, 1):
        ticket = test_case["ticket"]
        expected = test_case["expected"]
        reason = test_case["reason"]
        
        print(f"[{i}/{total}] Testing: {reason}")
        print(f"  Ticket: {ticket[:60]}...")
        
        result = classify_ticket(ticket, api_key)
        
        if "error" in result:
            print(f"  ❌ ERROR: {result['error']}")
            errors.append({
                "ticket": ticket,
                "expected": expected,
                "error": result['error'],
                "reason": reason
            })
            continue
        
        actual = result.get("category", "Unknown")
        confidence = result.get("confidence", 0)
        priority = result.get("priority", "unknown")
        provider = result.get("provider", "unknown")
        
        # Check category
        category_correct = actual == expected
        
        # Check priority if specified
        priority_correct = True
        if "expected_priority" in test_case:
            priority_correct = priority == test_case["expected_priority"]
        
        is_correct = category_correct and priority_correct
        
        if is_correct:
            print(f"  ✅ CORRECT: {actual} (confidence: {confidence}, priority: {priority}, provider: {provider})")
            correct += 1
        else:
            status_parts = []
            if not category_correct:
                status_parts.append(f"Expected: {expected}, Got: {actual}")
            if not priority_correct:
                status_parts.append(f"Expected priority: {test_case['expected_priority']}, Got: {priority}")
            
            print(f"  ❌ WRONG: {' | '.join(status_parts)}")
            print(f"     (confidence: {confidence}, provider: {provider})")
            
            errors.append({
                "ticket": ticket,
                "expected": expected,
                "actual": actual,
                "confidence": confidence,
                "priority": priority,
                "provider": provider,
                "reason": reason
            })
        
        print()
    
    # Summary
    accuracy = (correct / total) * 100
    print("=" * 80)
    print(f"RESULTS: {correct}/{total} correct ({accuracy:.1f}% accuracy)")
    print("=" * 80)
    print()
    
    if errors:
        print("ERRORS TO FIX:")
        print("-" * 80)
        for error in errors:
            print(f"❌ {error['reason']}")
            print(f"   Ticket: {error['ticket'][:70]}...")
            if 'actual' in error:
                print(f"   Expected: {error['expected']}")
                print(f"   Got: {error['actual']} (confidence: {error['confidence']}, provider: {error['provider']})")
            else:
                print(f"   Error: {error['error']}")
            print()
    
    # Save results
    with open("accuracy_test_results.json", "w") as f:
        json.dump({
            "total": total,
            "correct": correct,
            "accuracy": accuracy,
            "errors": errors
        }, f, indent=2)
    
    print(f"Results saved to accuracy_test_results.json")


if __name__ == "__main__":
    main()
