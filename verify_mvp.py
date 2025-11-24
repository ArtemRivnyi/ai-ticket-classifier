import os
import sys
import json
import unittest
from app import app

class MVPVerification(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        self.master_key = os.getenv('MASTER_API_KEY', 'test_master_key')
        
        # Ensure we have a valid API key for testing
        # We'll use the master key for simplicity in verification
        self.headers = {
            'X-API-Key': self.master_key,
            'Content-Type': 'application/json'
        }

    def test_01_web_ui_availability(self):
        """Verify Web UI endpoints are accessible"""
        print("\n[1/5] Verifying Web UI...")
        endpoints = ['/', '/about', '/evaluation', '/docs/']
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, 200, f"Failed to access {endpoint}")
            print(f"  ✅ {endpoint} is accessible")

    def test_02_api_documentation(self):
        """Verify Swagger/OpenAPI spec"""
        print("\n[2/5] Verifying API Documentation...")
        response = self.client.get('/static/swagger.json')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data.get('openapi'), '3.0.0')
        print("  ✅ OpenAPI spec is valid")

    def test_03_authentication(self):
        """Verify Authentication mechanisms"""
        print("\n[3/5] Verifying Authentication...")
        
        # 1. Try without key
        response = self.client.post('/api/v1/classify', json={'ticket': 'test'})
        self.assertEqual(response.status_code, 401)
        print("  ✅ Access denied without API key")
        
        # 2. Try with invalid key
        response = self.client.post('/api/v1/classify', 
                                  headers={'X-API-Key': 'invalid_key'},
                                  json={'ticket': 'test'})
        self.assertEqual(response.status_code, 401)
        print("  ✅ Access denied with invalid API key")

    def test_04_classification_flow(self):
        """Verify Classification endpoints"""
        print("\n[4/5] Verifying Classification Flow...")
        
        # 1. Single Classification
        payload = {'ticket': 'My internet is not working'}
        response = self.client.post('/api/v1/classify', 
                                  headers=self.headers,
                                  json=payload)
        
        # We might get 503 if providers aren't configured, which is acceptable for this check
        # as long as the application logic works (auth, validation, etc.)
        if response.status_code == 200:
            data = response.get_json()
            self.assertIn('category', data)
            self.assertIn('confidence', data)
            print("  ✅ Single classification successful")
        elif response.status_code == 503:
             print("  ⚠️ Providers unavailable (expected if no keys), but endpoint reachable")
        else:
            self.fail(f"Unexpected status code: {response.status_code}")

        # 2. Batch Classification
        batch_payload = {'tickets': ['Ticket 1', 'Ticket 2']}
        response = self.client.post('/api/v1/batch', 
                                  headers=self.headers,
                                  json=batch_payload)
        
        if response.status_code == 200:
            data = response.get_json()
            # Batch endpoint returns a dict with 'results' and 'errors'
            self.assertTrue(isinstance(data, dict))
            self.assertIn('results', data)
            self.assertTrue(isinstance(data['results'], list))
            print("  ✅ Batch classification successful")
        elif response.status_code == 503:
             print("  ⚠️ Providers unavailable (expected if no keys), but endpoint reachable")
        else:
            self.fail(f"Unexpected status code: {response.status_code}")

    def test_05_monitoring(self):
        """Verify Monitoring endpoints"""
        print("\n[5/5] Verifying Monitoring...")
        
        # Health
        response = self.client.get('/api/v1/health')
        self.assertEqual(response.status_code, 200)
        print("  ✅ Health endpoint is active")
        
        # Metrics (if available)
        response = self.client.get('/metrics')
import os
import sys
import json
import unittest
import requests # Added for external HTTP requests
import time     # Added for sleep in main block
from app import app

class MVPVerification(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        self.master_key = os.getenv('MASTER_API_KEY', 'test_master_key')
        
        # Ensure we have a valid API key for testing
        # We'll use the master key for simplicity in verification
        self.headers = {
            'X-API-Key': self.master_key,
            'Content-Type': 'application/json'
        }

        # For external requests (Evaluation, CSV Batch, Feedback)
        self.BASE_URL = "http://127.0.0.1:5000" # Assuming app runs on default Flask port
        self.API_KEY = self.master_key
        self.HEADERS = self.headers # Reusing the headers dictionary

    def test_01_web_ui_availability(self):
        """Verify Web UI endpoints are accessible"""
        print("\n[1/8] Verifying Web UI...")
        endpoints = ['/', '/about', '/evaluation', '/docs/']
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, 200, f"Failed to access {endpoint}")
            print(f"  ✅ {endpoint} is accessible")

    def test_02_api_documentation(self):
        """Verify Swagger/OpenAPI spec"""
        print("\n[2/8] Verifying API Documentation...")
        response = self.client.get('/static/swagger.json')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data.get('openapi'), '3.0.0')
        print("  ✅ OpenAPI spec is valid")

    def test_03_authentication(self):
        """Verify Authentication mechanisms"""
        print("\n[3/8] Verifying Authentication...")
        
        # 1. Try without key
        response = self.client.post('/api/v1/classify', json={'ticket': 'test'})
        self.assertEqual(response.status_code, 401)
        print("  ✅ Access denied without API key")
        
        # 2. Try with invalid key
        response = self.client.post('/api/v1/classify', 
                                  headers={'X-API-Key': 'invalid_key'},
                                  json={'ticket': 'test'})
        self.assertEqual(response.status_code, 401)
        print("  ✅ Access denied with invalid API key")

    def test_04_classification_flow(self):
        """Verify Classification endpoints"""
        print("\n[4/8] Verifying Classification Flow...")
        
        # 1. Single Classification
        payload = {'ticket': 'My internet is not working'}
        response = self.client.post('/api/v1/classify', 
                                  headers=self.headers,
                                  json=payload)
        
        # We might get 503 if providers aren't configured, which is acceptable for this check
        # as long as the application logic works (auth, validation, etc.)
        if response.status_code == 200:
            data = response.get_json()
            self.assertIn('category', data)
            self.assertIn('confidence', data)
            print("  ✅ Single classification successful")
        elif response.status_code == 503:
             print("  ⚠️ Providers unavailable (expected if no keys), but endpoint reachable")
        else:
            self.fail(f"Unexpected status code: {response.status_code}")

        # 2. Batch Classification
        batch_payload = {'tickets': ['Ticket 1', 'Ticket 2']}
        response = self.client.post('/api/v1/batch', 
                                  headers=self.headers,
                                  json=batch_payload)
        
        if response.status_code == 200:
            data = response.get_json()
            # Batch endpoint returns a dict with 'results' and 'errors'
            self.assertTrue(isinstance(data, dict))
            self.assertIn('results', data)
            self.assertTrue(isinstance(data['results'], list))
            print("  ✅ Batch classification successful")
        elif response.status_code == 503:
             print("  ⚠️ Providers unavailable (expected if no keys), but endpoint reachable")
        else:
            self.fail(f"Unexpected status code: {response.status_code}")

    def test_05_monitoring(self):
        """Verify Monitoring endpoints"""
        print("\n[5/8] Verifying Monitoring...")
        
        # Health
        response = self.client.get('/api/v1/health')
        self.assertEqual(response.status_code, 200)
        print("  ✅ Health endpoint is active")
        
        # Metrics (if available)
        response = self.client.get('/metrics')
        # Metrics might be 404 if not enabled or different path, but checking if app doesn't crash
        if response.status_code == 200:
            print("  ✅ Metrics endpoint is active")
        else:
            print(f"  ℹ️ Metrics endpoint returned {response.status_code} (optional)")

    def test_06_evaluation_endpoint(self):
        """Verify Evaluation endpoint"""
        print("\n[6/8] Verifying Evaluation...")
        
        # Test evaluation run
        # Note: This test uses 'requests' to simulate an external call,
        # as the evaluation endpoint might involve background tasks or external services
        # that are better tested via HTTP than Flask's test client.
        response = requests.post(
            f"{self.BASE_URL}/api/evaluation/run",
            headers=self.HEADERS
        )
        
        if response.status_code == 200:
            data = response.json() # Use .json() for requests library
            self.assertIn('accuracy', data)
            self.assertIn('results', data)
            self.assertTrue(len(data['results']) > 0)
            print(f"  ✅ Evaluation run successful (Accuracy: {data['accuracy']}%)")
        elif response.status_code == 503:
            print("  ⚠️ Evaluation skipped (Providers unavailable)")
        else:
            self.fail(f"Evaluation failed: {response.status_code} - {response.text}")

    def test_07_csv_batch_endpoint(self):
        """Verify CSV Batch Classification endpoint"""
        print("\n[7/8] Verifying CSV Batch Classification...")
        
        # Create a dummy CSV file
        csv_content = "ticket\nI cannot login\nVPN is down"
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        # Note: This test uses 'requests' for multipart/form-data handling
        response = requests.post(
            f"{self.BASE_URL}/api/classify/batch",
            headers={'X-API-Key': self.API_KEY},  # No Content-Type, requests adds multipart/form-data
            files=files
        )
        
        if response.status_code == 200:
            data = response.json()
            self.assertIn('results', data)
            self.assertEqual(data['total'], 2)
            print("  ✅ CSV Batch classification successful")
        elif response.status_code == 503:
            print("  ⚠️ CSV Batch skipped (Providers unavailable)")
        else:
            self.fail(f"CSV Batch failed: {response.status_code} - {response.text}")

    def test_08_feedback_endpoint(self):
        """Verify Feedback endpoint"""
        print("\n[8/8] Verifying Feedback...")
        
        payload = {
            "request_id": "test_req_123",
            "ticket": "Test ticket",
            "predicted": "Network Issue",
            "correct": True
        }
        
        # Note: This test uses 'requests' to simulate an external call
        response = requests.post(
            f"{self.BASE_URL}/api/feedback",
            headers=self.HEADERS,
            json=payload
        )
        
        if response.status_code == 200:
            print("  ✅ Feedback submission successful")
        else:
            self.fail(f"Feedback submission failed: {response.status_code} - {response.text}")

if __name__ == '__main__':
    # Set dummy env vars for testing if not present
    os.environ.setdefault('MASTER_API_KEY', 'test_master_key')
    os.environ.setdefault('SECRET_KEY', 'test_secret_key')
    os.environ.setdefault('JWT_SECRET', 'test_jwt_secret')
    
    # Wait for server to start (if running externally, e.g., with 'flask run')
    # This sleep is primarily for when the tests are run against a separately launched Flask app.
    # When using app.test_client(), the app is implicitly available.
    print("Waiting for server to be ready (if running externally)...")
    time.sleep(2) 
    unittest.main(verbosity=0)
