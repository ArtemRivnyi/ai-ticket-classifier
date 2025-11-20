import requests
import json
import time
import sys
import os

# Configuration
BASE_URL = "http://localhost:5000/api/v1"
API_KEY = None  # Will be registered dynamically

# Test Data - 50 Diverse Tickets
TEST_TICKETS = [
    # Authentication Issue
    {"text": "I cannot log in to my account.", "expected_category": "Authentication Issue", "expected_subcategory": "Login Failure"},
    {"text": "Forgot my password and reset link is not working.", "expected_category": "Authentication Issue", "expected_subcategory": "Password Reset"},
    {"text": "My 2FA code is invalid every time I try.", "expected_category": "Authentication Issue", "expected_subcategory": "2FA/MFA Issue"},
    {"text": "I'm getting logged out every 5 minutes.", "expected_category": "Authentication Issue", "expected_subcategory": "Session Expired"},
    {"text": "SSO login button is greyed out.", "expected_category": "Authentication Issue", "expected_subcategory": "Login Failure"},

    # Hardware Issue
    {"text": "The printer is jamming constantly.", "expected_category": "Hardware Issue", "expected_subcategory": "Device Malfunction"},
    {"text": "Card reader is not detecting any cards.", "expected_category": "Hardware Issue", "expected_subcategory": "Device Malfunction"},
    {"text": "Sensor battery drains in 2 hours.", "expected_category": "Hardware Issue", "expected_subcategory": "Battery/Power"},
    {"text": "Camera stopped working after the update.", "expected_category": "Hardware Issue", "expected_subcategory": "Device Malfunction"},
    {"text": "Device firmware update failed.", "expected_category": "Hardware Issue", "expected_subcategory": "Firmware"},

    # Billing Bug
    {"text": "I was charged twice for the same invoice.", "expected_category": "Billing Bug", "expected_subcategory": "Invoice Mismatch"},
    {"text": "Invoice shows $500 but card charged $5000.", "expected_category": "Billing Bug", "expected_subcategory": "Invoice Mismatch"},
    {"text": "Dashboard says 'Paid' but I got a dunning email.", "expected_category": "Billing Bug", "expected_subcategory": "UI/Backend Mismatch"},
    {"text": "Tax calculation is wrong on the checkout page.", "expected_category": "Billing Bug", "expected_subcategory": "Invoice Mismatch"},
    {"text": "Subscription status is 'Active' but features are locked.", "expected_category": "Billing Bug", "expected_subcategory": "UI/Backend Mismatch"},

    # Integration Issue
    {"text": "API returns 500 error on /users endpoint.", "expected_category": "Integration Issue", "expected_subcategory": "API Failure"},
    {"text": "Webhook is not triggering for new orders.", "expected_category": "Integration Issue", "expected_subcategory": "Webhook Error"},
    {"text": "Slack notifications are not coming through.", "expected_category": "Integration Issue", "expected_subcategory": "Third-party Service"},
    {"text": "Salesforce sync is stuck in 'Pending'.", "expected_category": "Integration Issue", "expected_subcategory": "Third-party Service"},
    {"text": "SDK throws timeout exception.", "expected_category": "Integration Issue", "expected_subcategory": "API Failure"},

    # Notification Issue
    {"text": "I didn't receive the welcome email.", "expected_category": "Notification Issue", "expected_subcategory": "Email Delivery"},
    {"text": "Email went to spam folder.", "expected_category": "Notification Issue", "expected_subcategory": "Email Delivery"},
    {"text": "SMS verification code never arrived.", "expected_category": "Notification Issue", "expected_subcategory": "Slack/SMS"},
    {"text": "Weekly report email is blank.", "expected_category": "Notification Issue", "expected_subcategory": "Email Delivery"},
    {"text": "Notifications are delayed by 2 hours.", "expected_category": "Notification Issue", "expected_subcategory": "Partial Delivery"},

    # Payment Issue
    {"text": "Transaction failed with error 404.", "expected_category": "Payment Issue", "expected_subcategory": "Transaction Failed"},
    {"text": "I need a refund for my last order.", "expected_category": "Payment Issue", "expected_subcategory": "Refund Request"},
    {"text": "I see a charge I don't recognize on my statement.", "expected_category": "Payment Issue", "expected_subcategory": "Unrecognized Charge"},
    {"text": "Credit card expired, how to update?", "expected_category": "Payment Issue", "expected_subcategory": "Transaction Failed"},
    {"text": "Payment declined but I have funds.", "expected_category": "Payment Issue", "expected_subcategory": "Transaction Failed"},

    # Account Problem
    {"text": "I need to change my email address.", "expected_category": "Account Problem", "expected_subcategory": "Profile Update"},
    {"text": "Wrong name on my profile.", "expected_category": "Account Problem", "expected_subcategory": "Profile Update"},
    {"text": "Cannot access the admin settings page.", "expected_category": "Account Problem", "expected_subcategory": "Permissions"},
    {"text": "Where are the account settings?", "expected_category": "Account Problem", "expected_subcategory": "Settings"},
    {"text": "Please delete my account.", "expected_category": "Account Problem", "expected_subcategory": "Settings"},

    # Bug/Technical Issue
    {"text": "App crashes when I click 'Save'.", "expected_category": "Bug/Technical Issue", "expected_subcategory": "Crash/Error"},
    {"text": "Page takes 30 seconds to load.", "expected_category": "Bug/Technical Issue", "expected_subcategory": "Performance"},
    {"text": "Button is misaligned on mobile view.", "expected_category": "Bug/Technical Issue", "expected_subcategory": "UI/UX Glitch"},
    {"text": "Search results are empty but I have data.", "expected_category": "Bug/Technical Issue", "expected_subcategory": "Crash/Error"},
    {"text": "Javascript error in console.", "expected_category": "Bug/Technical Issue", "expected_subcategory": "Crash/Error"},

    # Feature Request
    {"text": "Can you add a dark mode?", "expected_category": "Feature Request", "expected_subcategory": "New Feature"},
    {"text": "It would be nice to export to PDF.", "expected_category": "Feature Request", "expected_subcategory": "Improvement"},
    {"text": "Please add support for French language.", "expected_category": "Feature Request", "expected_subcategory": "New Feature"},
    {"text": "We need an API endpoint for user management.", "expected_category": "Feature Request", "expected_subcategory": "New Feature"},
    {"text": "Make the sidebar collapsible.", "expected_category": "Feature Request", "expected_subcategory": "Improvement"},

    # General Question
    {"text": "How do I change my password?", "expected_category": "General Question", "expected_subcategory": "How-to"},
    {"text": "Where is the documentation?", "expected_category": "General Question", "expected_subcategory": "Documentation"},
    {"text": "What is the pricing for Enterprise?", "expected_category": "General Question", "expected_subcategory": "Pricing/Sales"},
    {"text": "Do you offer a free trial?", "expected_category": "General Question", "expected_subcategory": "Pricing/Sales"},
    {"text": "Is there a tutorial video?", "expected_category": "General Question", "expected_subcategory": "How-to"},
]

def register_api_key():
    """Register a new API key for testing."""
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": "test_large@example.com",
            "name": "Test User",
            "organization": "Test Org",
            "tier": "professional"
        })
        if response.status_code == 201:
            key = response.json().get("api_key")
            print(f"✅ Registered API key: {key[:20]}...")
            return key
        else:
            print(f"❌ Failed to register API key: {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Connection error: {e}")
        sys.exit(1)

def run_tests():
    global API_KEY
    print("================================================================================")
    print("LARGE SCALE ACCURACY TEST - 50 Tickets")
    print("================================================================================")
    
    API_KEY = register_api_key()
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    
    correct_count = 0
    total_count = len(TEST_TICKETS)
    errors = []
    
    start_time = time.time()
    
    print(f"[{total_count}/{total_count}] Processing...")
    
    for i, case in enumerate(TEST_TICKETS):
        try:
            response = requests.post(
                f"{BASE_URL}/classify",
                headers=headers,
                json={"ticket": case["text"]}
            )
            
            if response.status_code == 200:
                result = response.json()
                predicted_category = result.get("category")
                predicted_subcategory = result.get("subcategory")
                
                # Check Category
                category_match = predicted_category == case["expected_category"]
                
                # Check Subcategory (if expected)
                subcategory_match = True
                if case.get("expected_subcategory"):
                    # Allow None if we didn't expect one, but if we did, it must match
                    if predicted_subcategory != case["expected_subcategory"]:
                        subcategory_match = False
                
                if category_match and subcategory_match:
                    correct_count += 1
                    # print(f"✅ {i+1}. Correct: {predicted_category} -> {predicted_subcategory}")
                else:
                    errors.append({
                        "text": case["text"],
                        "expected": f"{case['expected_category']} -> {case.get('expected_subcategory')}",
                        "got": f"{predicted_category} -> {predicted_subcategory} (Provider: {result.get('provider')})"
                    })
            else:
                errors.append({
                    "text": case["text"],
                    "expected": "200 OK",
                    "got": f"{response.status_code} {response.text}"
                })
                
        except Exception as e:
            errors.append({
                "text": case["text"],
                "expected": "Success",
                "got": f"Exception: {str(e)}"
            })
        
        # Add delay to avoid Gemini API rate limits (10 req/min = 6 seconds between requests)
        # Using 1.5 seconds as a compromise between speed and reliability
        if i < total_count - 1:  # Don't delay after the last request
            time.sleep(1.5)
            
    end_time = time.time()
    duration = end_time - start_time
    
    print("================================================================================")
    print(f"RESULTS: {correct_count}/{total_count} correct ({correct_count/total_count*100:.1f}% accuracy)")
    print(f"Time taken: {duration:.2f}s (Avg: {duration/total_count:.2f}s/ticket)")
    print("================================================================================")
    
    if errors:
        print("\n❌ ERRORS:")
        for error in errors:
            print(f"Ticket: {error['text']}")
            print(f"Expected: {error['expected']}")
            print(f"Got:      {error['got']}")
            print("-" * 40)
            
    if correct_count == total_count:
        print("\n🎉 PERFECT SCORE!")
        sys.exit(0)
    elif correct_count / total_count >= 0.9:
        print("\n✅ PASSED (>90%)")
        sys.exit(0)
    else:
        print("\n❌ FAILED (<90%)")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
