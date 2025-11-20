import google.generativeai as genai
import os
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

logger = logging.getLogger(__name__)

class GeminiClassifier:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")
        
        genai.configure(api_key=api_key)
        
        # Use Gemini 2.0 Flash for best performance
        try:
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info("Using gemini-2.0-flash-exp")
        except:
            try:
                self.model = genai.GenerativeModel('models/gemini-1.5-pro')
                logger.info("Using gemini-1.5-pro")
            except:
                self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
                logger.info("Using gemini-1.5-flash-latest")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,))
    )
    def classify(self, ticket_text):
        """Classify with retry logic and comprehensive prompt"""
        try:
            prompt = f"""You are an expert support ticket classifier. Classify the ticket into ONE category and ONE subcategory.

**STRICT RULES:**
1. Choose EXACTLY ONE category from the list below
2. Choose EXACTLY ONE subcategory within that category
3. NEVER invent new categories or subcategories
4. If unclear or ambiguous → use "Other" > "Unclassified"
5. Focus on the PRIMARY issue, ignore secondary mentions

**CATEGORIES & SUBCATEGORIES:**

1. Authentication Issue: Login Failure, 2FA/MFA Issue, Password Reset, Session Expired
2. Hardware Issue: Device Malfunction, Battery/Power, Connectivity (Hardware), Firmware
3. Billing Bug: Invoice Mismatch, UI/Backend Mismatch, Webhook Failure
4. Integration Issue: API Failure, Webhook Error, SSO/OAuth, Third-party Service
5. Notification Issue: Email Delivery, Slack/SMS, Partial Delivery
6. Payment Issue: Transaction Failed, Refund Request, Unrecognized Charge, Double Charge
7. Network Issue: Connectivity Loss, Latency/Slowness, VPN Issue, WiFi
8. Account Problem: Profile Update, Settings, Permissions
9. Bug/Technical Issue: Crash/Error, Performance, UI/UX Glitch
10. Security Incident: Unauthorized Access, Data Breach, Phishing
11. Feature Request: New Feature, Improvement, Configuration Change
12. General Question: How-to, Documentation, Pricing/Sales
13. Data / Reporting Issue: Data Accuracy, Report Generation, Missing Data
14. Mixed Issue: Multiple Issues
15. Spam / Abuse: Spam, Harassment
16. Other: Unclassified

**PATTERN HINTS:**
- "webhook", "API", "callback", "integration", "SDK" → Integration Issue
- "2FA", "OTP", "login", "password", "SSO", "OAuth" → Authentication Issue
- "slow", "lag", "performance", "freeze" → Bug/Technical Issue > Performance
- "declined", "invoice", "refund", "charge" → Payment Issue
- "dashboard shows X but charged Y" → Billing Bug
- "email not received", "notification missing" → Notification Issue

**FEW-SHOT EXAMPLES:**

Example 1:
Ticket: "My 2FA code is not working and I can't log in"
Category: Authentication Issue
Subcategory: 2FA/MFA Issue

Example 2:
Ticket: "Password reset link expired before I could use it"
Category: Authentication Issue
Subcategory: Password Reset

Example 3:
Ticket: "Dashboard shows paid but I got a dunning email"
Category: Billing Bug
Subcategory: UI/Backend Mismatch

Example 4:
Ticket: "Invoice shows $100 but I was charged $150"
Category: Billing Bug
Subcategory: Invoice Mismatch

Example 5:
Ticket: "Stripe webhook is timing out after 30 seconds"
Category: Integration Issue
Subcategory: Webhook Error

Example 6:
Ticket: "SSO login fails with 'invalid_grant' error"
Category: Integration Issue
Subcategory: SSO/OAuth

Example 7:
Ticket: "API returns 500 error when I try to create a user"
Category: Integration Issue
Subcategory: API Failure

Example 8:
Ticket: "Not receiving any email notifications"
Category: Notification Issue
Subcategory: Email Delivery

Example 9:
Ticket: "Half the team gets Slack alerts, half doesn't"
Category: Notification Issue
Subcategory: Partial Delivery

Example 10:
Ticket: "Payment was declined but my card works elsewhere"
Category: Payment Issue
Subcategory: Transaction Failed

Example 11:
Ticket: "I was charged twice for the same subscription"
Category: Payment Issue
Subcategory: Double Charge

Example 12:
Ticket: "Internet keeps dropping every 5 minutes"
Category: Network Issue
Subcategory: Connectivity Loss

Example 13:
Ticket: "App is very slow and laggy"
Category: Bug/Technical Issue
Subcategory: Performance

Example 14:
Ticket: "Firmware update failed on my device"
Category: Hardware Issue
Subcategory: Firmware

Example 15:
Ticket: "Someone accessed my account without permission"
Category: Security Incident
Subcategory: Unauthorized Access

**NOW CLASSIFY THIS TICKET:**
Ticket: "{ticket_text}"

**RESPONSE FORMAT (JSON):**
{{
  "category": "Category Name",
  "subcategory": "Subcategory Name",
  "confidence": 0.95
}}

Return ONLY valid JSON, nothing else."""

            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.1,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 100,
                }
            )
            
            result_text = response.text.strip()
            
            # Parse JSON response
            import json
            import re
            
            # Extract JSON from markdown code blocks if present
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(1)
            
            result = json.loads(result_text)
            
            logger.info(f"Gemini classification: {result.get('category')} > {result.get('subcategory')}")
            
            return {
                'category': result.get('category', 'Other'),
                'subcategory': result.get('subcategory', 'Unclassified'),
                'confidence': result.get('confidence', 0.85),
                'provider': 'gemini'
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {str(e)}, response: {result_text}")
            # Fallback: try to extract category from text
            return {
                'category': 'Other',
                'subcategory': 'Unclassified',
                'confidence': 0.5,
                'provider': 'gemini'
            }
        except Exception as e:
            logger.error(f"Classification error: {str(e)}")
            raise
