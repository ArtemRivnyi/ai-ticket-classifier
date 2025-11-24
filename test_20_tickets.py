#!/usr/bin/env python3
"""
Comprehensive test script for AI Ticket Classifier
Tests 20 diverse tickets covering all categories
"""

import requests
import json
import time
from typing import Dict, List

BASE_URL = "http://localhost:5000"
API_KEY = "local-master-key"

# 20 diverse test tickets covering all categories
TEST_TICKETS = [
    # Authentication Issues (4)
    {
        "ticket": "I cannot log in. The verification code is invalid.",
        "expected_category": "Authentication Issue",
        "expected_priority": "high"
    },
    {
        "ticket": "Reset link expired before I could use it.",
        "expected_category": "Authentication Issue",
        "expected_priority": "medium"
    },
    {
        "ticket": "Two-factor authentication not working on mobile app",
        "expected_category": "Authentication Issue",
        "expected_priority": "high"
    },
    {
        "ticket": "Password reset email never arrived",
        "expected_category": "Authentication Issue",
        "expected_priority": "high"
    },
    
    # Billing Issues (4)
    {
        "ticket": "I was charged twice for the same subscription.",
        "expected_category": "Billing Issue",
        "expected_priority": "critical"
    },
    {
        "ticket": "Invoice says $100 but processor charged $150.",
        "expected_category": "Billing Issue",
        "expected_priority": "critical"
    },
    {
        "ticket": "Need to update payment method for recurring subscription",
        "expected_category": "Billing Issue",
        "expected_priority": "medium"
    },
    {
        "ticket": "Refund not received after cancellation 2 weeks ago",
        "expected_category": "Billing Issue",
        "expected_priority": "high"
    },
    
    # Hardware Issues (3)
    {
        "ticket": "Camera stopped working after firmware update.",
        "expected_category": "Hardware Issue",
        "expected_priority": "high"
    },
    {
        "ticket": "Laptop screen flickering and showing vertical lines",
        "expected_category": "Hardware Issue",
        "expected_priority": "high"
    },
    {
        "ticket": "Printer not connecting via USB cable",
        "expected_category": "Hardware Issue",
        "expected_priority": "high"
    },
    
    # Integration Issues (2)
    {
        "ticket": "Slack integration only sends alerts to half of our team.",
        "expected_category": "Integration Issue",
        "expected_priority": "high"
    },
    {
        "ticket": "Salesforce sync failing with error 500",
        "expected_category": "Integration Issue",
        "expected_priority": "high"
    },
    
    # Network Issues (3)
    {
        "ticket": "My internet connection keeps dropping every time I try to join a video call.",
        "expected_category": "Network Issue",
        "expected_priority": "high"
    },
    {
        "ticket": "Email notifications not delivered to some users.",
        "expected_category": "Notification Issue",
        "expected_priority": "medium"
    },
    {
        "ticket": "VPN connection timeout after 5 minutes",
        "expected_category": "Network Issue",
        "expected_priority": "high"
    },
    
    # Mixed/Complex Issues (2)
    {
        "ticket": "Cannot log in AND my payment failed. Two separate issues.",
        "expected_category": "Mixed Issue",
        "expected_priority": "critical"
    },
    {
        "ticket": "App crashes when trying to export data and also billing shows wrong amount",
        "expected_category": "Mixed Issue",
        "expected_priority": "critical"
    },
    
    # Feature Requests (2)
    {
        "ticket": "Nice to have: add animation to the loading screen.",
        "expected_category": "Feature Request",
        "expected_priority": "low"
    },
    {
        "ticket": "Would be great to have dark mode support",
        "expected_category": "Feature Request",
        "expected_priority": "low"
    }
]


def classify_ticket(ticket_text: str) -> Dict:
    """Classify a single ticket using the API"""
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    payload = {"ticket": ticket_text}
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/classify",
            headers=headers,
            json=payload,
            timeout=15
        )
        duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            result['response_time'] = duration
            return result
        else:
            return {
                "error": f"HTTP {response.status_code}",
                "message": response.text
            }
    except Exception as e:
        return {"error": str(e)}


def test_all_tickets():
    """Test all 20 tickets and generate report"""
    print("=" * 80)
    print("AI TICKET CLASSIFIER - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print(f"\nTesting {len(TEST_TICKETS)} diverse tickets...\n")
    
    results = []
    correct_category = 0
    correct_priority = 0
    total_time = 0
    
    for i, test_case in enumerate(TEST_TICKETS, 1):
        ticket_text = test_case["ticket"]
        expected_cat = test_case["expected_category"]
        expected_pri = test_case["expected_priority"]
        
        print(f"\n[{i}/20] Testing: {ticket_text[:60]}...")
        
        result = classify_ticket(ticket_text)
        
        if "error" in result:
            print(f"   ❌ ERROR: {result['error']}")
            results.append({
                "test_num": i,
                "ticket": ticket_text,
                "status": "FAILED",
                "error": result.get("error", "Unknown")
            })
            continue
        
        # Extract results
        actual_cat = result.get("category", "Unknown")
        actual_pri = result.get("priority", "Unknown")
        confidence = result.get("confidence", 0) * 100
        provider = result.get("provider", "Unknown")
        response_time = result.get("response_time", 0)
        
        total_time += response_time
        
        # Check accuracy
        cat_match = actual_cat == expected_cat
        pri_match = actual_pri == expected_pri
        
        if cat_match:
            correct_category += 1
        if pri_match:
            correct_priority += 1
        
        # Display result
        cat_icon = "✅" if cat_match else "❌"
        pri_icon = "✅" if pri_match else "❌"
        
        print(f"   {cat_icon} Category: {actual_cat} (expected: {expected_cat})")
        print(f"   {pri_icon} Priority: {actual_pri} (expected: {expected_pri})")
        print(f"   📊 Confidence: {confidence:.0f}% | Provider: {provider} | Time: {response_time:.2f}s")
        
        results.append({
            "test_num": i,
            "ticket": ticket_text,
            "expected_category": expected_cat,
            "actual_category": actual_cat,
            "expected_priority": expected_pri,
            "actual_priority": actual_pri,
            "confidence": confidence,
            "provider": provider,
            "response_time": response_time,
            "category_match": cat_match,
            "priority_match": pri_match
        })
        
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    # Generate summary report
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if "error" not in r)
    
    print(f"\n📋 Total Tests: {total_tests}")
    print(f"✅ Successful: {successful_tests}")
    print(f"❌ Failed: {total_tests - successful_tests}")
    
    if successful_tests > 0:
        cat_accuracy = (correct_category / successful_tests) * 100
        pri_accuracy = (correct_priority / successful_tests) * 100
        avg_time = total_time / successful_tests
        avg_confidence = sum(r.get("confidence", 0) for r in results if "confidence" in r) / successful_tests
        
        print(f"\n🎯 Category Accuracy: {cat_accuracy:.1f}% ({correct_category}/{successful_tests})")
        print(f"🎯 Priority Accuracy: {pri_accuracy:.1f}% ({correct_priority}/{successful_tests})")
        print(f"⚡ Average Response Time: {avg_time:.2f}s")
        print(f"📊 Average Confidence: {avg_confidence:.1f}%")
        
        # Provider breakdown
        providers = {}
        for r in results:
            if "provider" in r:
                prov = r["provider"]
                providers[prov] = providers.get(prov, 0) + 1
        
        print(f"\n🔧 Provider Usage:")
        for prov, count in providers.items():
            print(f"   - {prov}: {count} tickets ({count/successful_tests*100:.1f}%)")
    
    # Save detailed results to JSON
    with open("test_results.json", "w") as f:
        json.dump({
            "summary": {
                "total_tests": total_tests,
                "successful": successful_tests,
                "failed": total_tests - successful_tests,
                "category_accuracy": f"{cat_accuracy:.1f}%" if successful_tests > 0 else "N/A",
                "priority_accuracy": f"{pri_accuracy:.1f}%" if successful_tests > 0 else "N/A",
                "avg_response_time": f"{avg_time:.2f}s" if successful_tests > 0 else "N/A"
            },
            "detailed_results": results
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: test_results.json")
    print("=" * 80)


if __name__ == "__main__":
    test_all_tickets()
