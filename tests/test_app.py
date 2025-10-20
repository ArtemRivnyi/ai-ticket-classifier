import requests
import time
import sys

BASE_URL = "http://localhost:5000/api/v1"

def wait_for_health(timeout=30):
    """Wait for /health to return 200"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=5)
            if r.status_code == 200:
                print("✅ Health check passed")
                return True
        except requests.exceptions.RequestException as e:
            print(f"Waiting for server... ({e})")
        time.sleep(2)
    print("❌ Health check timeout")
    return False

def test_health_check():
    """Test that /health returns 200"""
    assert wait_for_health(), "Health check did not return 200 within timeout"

def test_classify_endpoint():
    """Test /classify endpoint"""
    payload = {"ticket": "I forgot my password"}
    try:
        r = requests.post(f"{BASE_URL}/classify", json=payload, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        response_json = r.json()
        assert "category" in response_json, "Response missing 'category' field"
        print(f"✅ Classification test passed - Category: {response_json['category']}")
    except Exception as e:
        print(f"❌ Classification test failed: {e}")
        raise

if __name__ == "__main__":
    try:
        test_health_check()
        test_classify_endpoint()
        print("🎉 All tests passed!")
    except Exception as e:
        print(f"💥 Tests failed: {e}")
        sys.exit(1)