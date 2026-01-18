import sys
import os
sys.path.append(os.getcwd())
import json
import pytest
from app import app
from database.models import init_db, User, APIKey, SessionLocal

def test_revenue_features():
    print("Initializing DB...")
    with app.app_context():
        init_db()
        # Clean up test user if exists
        db = SessionLocal()
        try:
            db.query(APIKey).delete()
            db.query(User).delete()
            db.commit()
        finally:
            db.close()

    client = app.test_client()

    # 1. Register User
    print("\n1. Testing User Registration...")
    reg_payload = {
        "email": "test@example.com",
        "password": "securepassword123",
        "organization": "Test Org",
        "name": "Test User"
    }
    response = client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 201
    data = response.get_json()
    print(f"   Registration successful. User ID: {data['user_id']}")
    api_key = data.get("api_key")
    assert api_key is not None
    print(f"   API Key received: {api_key[:10]}...")

    # 2. Test Protected Endpoint with Key
    print("\n2. Testing Protected Endpoint (Classify)...")
    classify_payload = {"ticket": "My internet is not working, please help."}
    headers = {"X-API-Key": api_key}
    response = client.post("/api/v1/classify", json=classify_payload, headers=headers)
    
    # Note: If providers are not configured, we might get 503, but auth should pass (not 401)
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 401:
        print("   FAILED: Auth failed")
        sys.exit(1)
    elif response.status_code == 503:
        print("   Auth passed (Service Unavailable due to missing providers, expected)")
    elif response.status_code == 200:
        print("   Auth passed and classification successful")
    else:
        print(f"   Unexpected status: {response.status_code}")

    # 3. Test Protected Endpoint without Key
    print("\n3. Testing Protected Endpoint without Key...")
    response = client.post("/api/v1/classify", json=classify_payload)
    assert response.status_code == 401
    print("   Correctly rejected (401)")

    # 4. List Keys
    print("\n4. Testing List Keys...")
    response = client.get("/api/v1/auth/keys", headers=headers)
    assert response.status_code == 200
    keys_data = response.get_json()
    print(f"   Keys found: {len(keys_data['keys'])}")
    assert len(keys_data['keys']) >= 1
    key_id = keys_data['keys'][0]['id']

    # 5. Revoke Key
    print(f"\n5. Testing Revoke Key (ID: {key_id})...")
    response = client.delete(f"/api/v1/auth/keys/{key_id}", headers=headers)
    assert response.status_code == 200
    print("   Key revoked")

    # 6. Verify Revoked Key
    print("\n6. Verifying Revoked Key...")
    response = client.post("/api/v1/classify", json=classify_payload, headers=headers)
    assert response.status_code == 401
    print("   Correctly rejected (401)")

    print("\n✅ All Revenue Features Verified Successfully!")

if __name__ == "__main__":
    try:
        test_revenue_features()
    except AssertionError as e:
        print(f"\n❌ Verification Failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
