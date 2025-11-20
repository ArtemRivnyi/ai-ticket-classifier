#!/usr/bin/env python3
"""
Test rule engine locally without Docker
"""

import sys
sys.path.insert(0, 'c:\\Projects\\AI tickets classifier PROJECT\\ai-ticket-classifier')

from providers.multi_provider import RuleBasedClassifier

# Initialize classifier
classifier = RuleBasedClassifier()

# Test cases from the checklist
TEST_CASES = [
    ("I cannot log in. The verification code is invalid.", "Authentication Issue"),
    ("Reset link expired before I could use it.", "Authentication Issue"),
    ("2FA verification failed. Cannot access my account.", "Authentication Issue"),
    
    ("I was charged twice for the same subscription.", "Payment Issue"),
    ("Payment completed but I want a refund.", "Payment Issue"),
    ("Unauthorized payment of $500 appeared on my card.", "Payment Issue"),
    
    ("Camera stopped working after firmware update.", "Hardware Issue"),
    ("Sensor battery drains in one hour.", "Hardware Issue"),
    ("Printer keeps jamming. Already cleaned it twice.", "Hardware Issue"),
    ("Card reader not detecting cards anymore.", "Hardware Issue"),
    
    ("Slack integration only sends alerts to half of our team.", "Notification Issue"),
    ("Webhook callbacks timing out. API not responding.", "Integration Issue"),
    ("SSO login with Azure AD failing. Error: invalid_grant.", "Integration Issue"),
    
    ("UI shows paid but Stripe webhook shows failed.", "Billing Bug"),
    ("Invoice says $100 but processor charged $150.", "Billing Bug"),
    ("Dashboard shows paid subscription but backend logs show unpaid.", "Billing Bug"),
    
    ("Email notifications not delivered to some users.", "Notification Issue"),
    ("Half of the team gets Slack alerts, the other half doesn't.", "Notification Issue"),
    
    ("Cannot log in AND my payment failed. Two separate issues.", "Mixed Issue"),
    
    ("Minor cosmetic issue with button alignment. Not urgent.", "Bug/Technical Issue"),
    ("Nice to have: add animation to the loading screen.", "Feature Request"),
]

print("=" * 80)
print("RULE ENGINE TEST - Local Testing")
print("=" * 80)
print()

correct = 0
total = len(TEST_CASES)

for i, (ticket, expected) in enumerate(TEST_CASES, 1):
    result = classifier.classify(ticket)
    category = result['category'] if result else 'None'
    
    # Check if expected category matches
    is_correct = category == expected
    
    if is_correct:
        print(f"[{i}/{total}] ✅ CORRECT: {expected}")
        print(f"  Ticket: {ticket[:60]}...")
        print(f"  Category: {category}")
        correct += 1
    else:
        print(f"[{i}/{total}] ❌ WRONG: Expected {expected}, Got {category}")
        print(f"  Ticket: {ticket[:60]}...")
    print()

accuracy = (correct / total) * 100
print("=" * 80)
print(f"RULE ENGINE ACCURACY: {correct}/{total} ({accuracy:.1f}%)")
print("=" * 80)
