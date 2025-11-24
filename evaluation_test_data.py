# Test data for evaluation - Updated to match actual classifier categories
TEST_TICKETS = [
    {"text": "I can't login to my account", "expected": "Authentication Issue", "priority": "high"},
    {"text": "VPN connection drops every 5 minutes", "expected": "Network Issue", "priority": "medium"},
    {"text": "Refund for order #12345 not received", "expected": "Billing Issue", "priority": "high"},
    {"text": "Request dark mode feature", "expected": "Feature Request", "priority": "low"},
    {"text": "Printer not working on 3rd floor", "expected": "Hardware Issue", "priority": "medium"},
    {"text": "How do I reset my password?", "expected": "General Question", "priority": "low"},  # Changed from Account Problem
    {"text": "Internet is very slow today", "expected": "Network Issue", "priority": "medium"},
    {"text": "I was charged twice for the same item", "expected": "Billing Issue", "priority": "critical"},  # Changed from high
    {"text": "Can you add a export to PDF button?", "expected": "Feature Request", "priority": "low"},
    {"text": "Mouse is broken", "expected": "Hardware Issue", "priority": "low"},
    {"text": "System is down", "expected": "Bug/Technical Issue", "priority": "critical"},
    {"text": "Where can I find the user manual?", "expected": "General Question", "priority": "low"},
    {"text": "My screen is flickering", "expected": "Hardware Issue", "priority": "medium"},
    {"text": "I need to update my billing address", "expected": "Account Problem", "priority": "low"},
    {"text": "The application crashes when I click save", "expected": "Bug/Technical Issue", "priority": "high"},
    {"text": "Wifi password is not working", "expected": "Network Issue", "priority": "high"},
    {"text": "I want to cancel my subscription", "expected": "Account Problem", "priority": "high"},
    {"text": "Is there a discount for students?", "expected": "General Question", "priority": "low"},
    {"text": "The server is not responding", "expected": "Bug/Technical Issue", "priority": "critical"},
    {"text": "I cannot access the shared drive", "expected": "Network Issue", "priority": "high"},
    {"text": "My keyboard keys are stuck", "expected": "Hardware Issue", "priority": "low"},
    {"text": "Please add support for French language", "expected": "Feature Request", "priority": "low"},
    {"text": "Invoice #999 is incorrect", "expected": "Billing Issue", "priority": "high"},
    {"text": "How do I change my profile picture?", "expected": "General Question", "priority": "low"},
    {"text": "Login page is throwing 500 error", "expected": "Bug/Technical Issue", "priority": "critical"},
    {"text": "I need a new laptop charger", "expected": "Hardware Issue", "priority": "medium"},
    {"text": "Payment gateway is timing out", "expected": "Billing Issue", "priority": "critical"},
    {"text": "Can we integrate with Slack?", "expected": "Feature Request", "priority": "low"},
    {"text": "My account is locked", "expected": "Authentication Issue", "priority": "high"},  # Changed from Account Problem
    {"text": "What are your support hours?", "expected": "General Question", "priority": "low"}
]
