import requests
import time

BASE_URL = "http://localhost:5000"

def wait_for_health(timeout=20):
    """Ждём, пока /health вернёт 200"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=2)
            if r.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    return False


def test_health_check():
    """Проверяем, что /health возвращает 200"""
    assert wait_for_health(), "Health check did not return 200 within timeout"


def test_classify_endpoint():
    """Проверяем /classify — API должен ответить JSON"""
    payload = {"ticket": "I forgot my password"}
    r = requests.post(f"{BASE_URL}/classify", json=payload, timeout=10)
    assert r.status_code == 200
    assert "category" in r.json()
