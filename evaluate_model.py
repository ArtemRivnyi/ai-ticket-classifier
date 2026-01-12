import csv
import json
import time
import os
import sys

# from tabulate import tabulate

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(env_path)
print(f"DEBUG: Loading .env from {env_path}")
print(f"DEBUG: GEMINI_API_KEY present: {'GEMINI_API_KEY' in os.environ}")

from providers.multi_provider import MultiProvider


def evaluate():
    print(f"🚀 Starting local evaluation using MultiProvider...")

    # Initialize provider
    try:
        provider = MultiProvider()
        print("✅ MultiProvider initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize MultiProvider: {e}")
        return

    results = []
    correct_count = 0
    total_count = 0

    with open("data/test_dataset.csv", "r") as f:
        reader = csv.DictReader(f)
        tickets = list(reader)
        total_count = len(tickets)

        print(f"📊 Found {total_count} test tickets.")

        for i, ticket in enumerate(tickets):
            text = ticket["text"]
            expected_category = ticket["expected_category"]
            expected_priority = ticket["expected_priority"]

            print(f"[{i+1}/{total_count}] Processing: {text[:50]}...")

            try:
                start_time = time.time()
                # Direct classification call
                data = provider.classify(text)
                duration = time.time() - start_time

                predicted_category = data.get("category")
                predicted_priority = data.get("priority").lower()
                confidence = data.get("confidence", 0)

                # Normalize for comparison
                is_correct_category = predicted_category == expected_category
                # Priority might be case sensitive or have slight variations
                is_correct_priority = predicted_priority == expected_priority.lower()

                if is_correct_category:
                    correct_count += 1

                results.append(
                    {
                        "text": text,
                        "expected": expected_category,
                        "predicted": predicted_category,
                        "confidence": confidence,
                        "correct": is_correct_category,
                        "latency": duration,
                        "provider": data.get("provider"),
                    }
                )

            except Exception as e:
                print(f"❌ Exception: {e}")
                results.append(
                    {
                        "text": text,
                        "expected": expected_category,
                        "predicted": "ERROR",
                        "confidence": 0,
                        "correct": False,
                        "latency": 0,
                        "provider": "error",
                    }
                )

    accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0
    avg_latency = (
        sum(r["latency"] for r in results) / total_count if total_count > 0 else 0
    )

    print("\n" + "=" * 50)
    print(f"🏁 Evaluation Complete")
    print(f"✅ Accuracy: {accuracy:.2f}%")
    print(f"⏱️ Avg Latency: {avg_latency:.3f}s")
    print("=" * 50)

    # Save results to JSON for the frontend to consume
    output = {
        "metrics": {
            "accuracy": accuracy,
            "total_tickets": total_count,
            "correct_tickets": correct_count,
            "avg_latency": avg_latency,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "results": results,
    }

    with open("data/evaluation_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print("💾 Results saved to data/evaluation_results.json")


if __name__ == "__main__":
    evaluate()
