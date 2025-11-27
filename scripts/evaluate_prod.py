import csv
import json
import time
import requests
import sys

# Live URL
BASE_URL = "https://ai-ticket-classifier-production.up.railway.app"
API_KEY = "sk_ORulUQRLvLHAueF3Ht1gXj9gTsY7xme3QD-UeVrO8nY"

def evaluate_prod():
    print(f"🚀 Starting PRODUCTION evaluation against {BASE_URL}...")
    
    results = []
    correct_count = 0
    total_count = 0
    
    try:
        with open('test_dataset.csv', 'r') as f:
            reader = csv.DictReader(f)
            tickets = list(reader)
            total_count = len(tickets)
            
            print(f"📊 Found {total_count} test tickets.")
            
            for i, ticket in enumerate(tickets):
                text = ticket['text']
                expected_category = ticket['expected_category']
                expected_priority = ticket['expected_priority']
                
                print(f"[{i+1}/{total_count}] Processing: {text[:50]}...")
                
                try:
                    start_time = time.time()
                    
                    headers = {
                        "Content-Type": "application/json",
                        "X-API-Key": API_KEY
                    }
                    payload = {"ticket": text}
                    
                    response = requests.post(
                        f"{BASE_URL}/api/v1/classify", 
                        headers=headers, 
                        json=payload, 
                        timeout=30
                    )
                    
                    duration = time.time() - start_time
                    
                    if response.status_code == 200:
                        data = response.json()
                        predicted_category = data.get('category')
                        predicted_priority = data.get('priority', '').lower()
                        confidence = data.get('confidence', 0)
                        provider = data.get('provider', 'unknown')
                    else:
                        print(f"❌ API Error: {response.status_code} - {response.text}")
                        predicted_category = "ERROR"
                        predicted_priority = "error"
                        confidence = 0
                        provider = "error"

                    # Normalize for comparison
                    is_correct_category = predicted_category == expected_category
                    
                    if is_correct_category:
                        correct_count += 1
                    else:
                        print(f"❌ Mismatch! Expected: {expected_category}, Got: {predicted_category} (Provider: {provider})")
                    
                    results.append({
                        "text": text,
                        "expected": expected_category,
                        "predicted": predicted_category,
                        "confidence": confidence,
                        "correct": is_correct_category,
                        "latency": duration,
                        "provider": provider
                    })
                    
                    # Rate limiting niceness
                    time.sleep(0.2)
                    
                except Exception as e:
                    print(f"❌ Exception: {e}")
                    results.append({
                        "text": text,
                        "expected": expected_category,
                        "predicted": "ERROR",
                        "confidence": 0,
                        "correct": False,
                        "latency": 0,
                        "provider": "error"
                    })
        
        accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0
        avg_latency = sum(r['latency'] for r in results) / total_count if total_count > 0 else 0
        
        print("\n" + "="*50)
        print(f"🏁 Production Evaluation Complete")
        print(f"✅ Accuracy: {accuracy:.2f}%")
        print(f"⏱️ Avg Latency: {avg_latency:.3f}s")
        print("="*50)
        
        # Save results
        output = {
            "metrics": {
                "accuracy": accuracy,
                "total_tickets": total_count,
                "correct_tickets": correct_count,
                "avg_latency": avg_latency,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "results": results
        }
        
        with open('prod_evaluation_results.json', 'w') as f:
            json.dump(output, f, indent=2)
        
        print("💾 Results saved to prod_evaluation_results.json")

    except FileNotFoundError:
        print("❌ test_dataset.csv not found!")

if __name__ == "__main__":
    evaluate_prod()
