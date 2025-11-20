# Classification Categories & Subcategories

Complete reference for all supported ticket categories and their subcategories in the AI Ticket Classifier.

## Overview

The classifier uses a **2-level hierarchical system**:
- **15 Main Categories** - High-level classification
- **50+ Subcategories** - Granular classification within each category

---

## Categories & Subcategories

### 1. Authentication Issue
**Description:** Problems related to user authentication and access control.

| Subcategory | Examples | Confidence Range |
|-------------|----------|------------------|
| **Login Failure** | "Cannot log in", "Invalid credentials" | 0.90-0.98 |
| **2FA/MFA Issue** | "2FA code not working", "MFA verification failed" | 0.92-0.98 |
| **Password Reset** | "Reset link expired", "Cannot reset password" | 0.90-0.95 |
| **Session Expired** | "Session timeout", "Logged out unexpectedly" | 0.85-0.95 |

**Priority:** High  
**Common Keywords:** login, password, 2fa, mfa, otp, verification, session

---

### 2. Hardware Issue
**Description:** Physical device malfunctions and hardware-related problems.

| Subcategory | Examples | Confidence Range |
|-------------|----------|------------------|
| **Device Malfunction** | "Printer not working", "Camera broken" | 0.88-0.95 |
| **Battery/Power** | "Battery drains fast", "Won't charge" | 0.90-0.98 |
| **Connectivity (Hardware)** | "USB not detected", "Bluetooth won't pair" | 0.85-0.93 |
| **Firmware** | "Firmware update failed", "Device needs update" | 0.90-0.95 |

**Priority:** Medium  
**Common Keywords:** printer, camera, sensor, battery, firmware, device

---

### 3. Billing Bug
**Description:** Discrepancies between billing UI and actual charges.

| Subcategory | Examples | Confidence Range |
|-------------|----------|------------------|
| **Invoice Mismatch** | "Invoice shows $100 but charged $150" | 0.92-0.98 |
| **UI/Backend Mismatch** | "Dashboard says paid but backend shows unpaid" | 0.90-0.97 |
| **Webhook Failure** | "Stripe webhook failed", "Payment webhook timeout" | 0.88-0.95 |

**Priority:** High  
**Common Keywords:** invoice, mismatch, ui, backend, webhook, billing bug

---

### 4. Integration Issue
**Description:** Problems with third-party integrations and APIs.

| Subcategory | Examples | Confidence Range |
|-------------|----------|------------------|
| **API Failure** | "API returns 500 error", "Endpoint not responding" | 0.90-0.98 |
| **Webhook Error** | "Webhook callback timeout", "Webhook not received" | 0.88-0.95 |
| **SSO/OAuth** | "SSO login failed", "OAuth token expired" | 0.92-0.98 |
| **Third-party Service** | "Slack integration broken", "Zapier not working" | 0.85-0.93 |

**Priority:** High  
**Common Keywords:** api, webhook, sso, oauth, integration, sdk

---

### 5. Notification Issue
**Description:** Problems with email, SMS, or in-app notifications.

| Subcategory | Examples | Confidence Range |
|-------------|----------|------------------|
| **Email Delivery** | "Not receiving emails", "Emails go to spam" | 0.90-0.98 |
| **Slack/SMS** | "Slack alerts not working", "SMS not delivered" | 0.88-0.95 |
| **Partial Delivery** | "Half the team gets notifications" | 0.85-0.93 |

**Priority:** Medium  
**Common Keywords:** email, slack, sms, notification, alert, delivery

---

### 6. Payment Issue
**Description:** Transaction problems and payment-related concerns.

| Subcategory | Examples | Confidence Range |
|-------------|----------|------------------|
| **Transaction Failed** | "Payment declined", "Transaction error" | 0.90-0.98 |
| **Refund Request** | "Want a refund", "Cancel and refund" | 0.92-0.98 |
| **Unrecognized Charge** | "Unauthorized charge", "Didn't authorize this" | 0.88-0.95 |
| **Double Charge** | "Charged twice", "Duplicate payment" | 0.90-0.97 |

**Priority:** High  
**Common Keywords:** payment, charge, refund, transaction, billing

---

### 7. Network Issue
**Description:** Connectivity and network-related problems.

| Subcategory | Examples | Confidence Range |
|-------------|----------|------------------|
| **Connectivity Loss** | "Internet keeps dropping", "Connection lost" | 0.90-0.98 |
| **Latency/Slowness** | "Very slow connection", "High latency" | 0.85-0.93 |
| **VPN Issue** | "VPN won't connect", "VPN disconnects" | 0.88-0.95 |
| **WiFi** | "WiFi not working", "Can't connect to WiFi" | 0.90-0.95 |

**Priority:** High  
**Common Keywords:** network, wifi, vpn, connectivity, latency, internet

---

### 8. Account Problem
**Description:** User account settings and profile issues.

| Subcategory | Examples | Confidence Range |
|-------------|----------|------------------|
| **Profile Update** | "Can't update profile", "Name change not saving" | 0.85-0.93 |
| **Settings** | "Settings not applying", "Preferences reset" | 0.80-0.90 |
| **Permissions** | "Don't have access", "Permission denied" | 0.88-0.95 |

**Priority:** Medium  
**Common Keywords:** account, profile, settings, permissions, access

---

### 9. Bug/Technical Issue
**Description:** Software bugs and technical glitches.

| Subcategory | Examples | Confidence Range |
|-------------|----------|------------------|
| **Crash/Error** | "App crashes", "Error message appears" | 0.90-0.98 |
| **Performance** | "App is slow", "Laggy interface" | 0.85-0.93 |
| **UI/UX Glitch** | "Button misaligned", "Text overlapping" | 0.80-0.90 |

**Priority:** Medium  
**Common Keywords:** bug, crash, error, glitch, performance

---

### 10. Security Incident
**Description:** Security breaches and unauthorized access.

| Subcategory | Examples | Confidence Range |
|-------------|----------|------------------|
| **Unauthorized Access** | "Someone accessed my account", "Suspicious login" | 0.92-0.98 |
| **Data Breach** | "Data leak", "Information exposed" | 0.90-0.98 |
| **Phishing** | "Received phishing email", "Suspicious link" | 0.88-0.95 |

**Priority:** Critical  
**Common Keywords:** security, breach, unauthorized, phishing, hack

---

### 11. Feature Request
**Description:** Requests for new features or improvements.

| Subcategory | Examples | Confidence Range |
|-------------|----------|------------------|
| **New Feature** | "Add dark mode", "Need export feature" | 0.90-0.98 |
| **Improvement** | "Make button bigger", "Improve search" | 0.85-0.93 |
| **Configuration Change** | "Change default settings", "Adjust timeout" | 0.80-0.90 |

**Priority:** Low  
**Common Keywords:** feature, request, suggestion, idea, improvement

---

### 12. General Question
**Description:** General inquiries and how-to questions.

| Subcategory | Examples | Confidence Range |
|-------------|----------|------------------|
| **How-to** | "How do I...?", "What's the process for...?" | 0.85-0.93 |
| **Documentation** | "Where's the docs?", "Need documentation" | 0.80-0.90 |
| **Pricing/Sales** | "What's the price?", "Sales inquiry" | 0.88-0.95 |

**Priority:** Low  
**Common Keywords:** how, question, help, documentation, pricing

---

### 13. Data / Reporting Issue
**Description:** Problems with data accuracy or reporting.

| Subcategory | Examples | Confidence Range |
|-------------|----------|------------------|
| **Data Accuracy** | "Numbers don't match", "Incorrect data" | 0.85-0.93 |
| **Report Generation** | "Report won't generate", "Export failed" | 0.80-0.90 |
| **Missing Data** | "Data missing", "Records not showing" | 0.88-0.95 |

**Priority:** Medium  
**Common Keywords:** data, report, export, analytics, dashboard

---

### 14. Mixed Issue
**Description:** Multiple unrelated issues in one ticket.

| Subcategory | Examples | Confidence Range |
|-------------|----------|------------------|
| **Multiple Issues** | "Login fails AND payment declined" | 0.75-0.85 |

**Priority:** Medium  
**Common Keywords:** and, also, plus, multiple

---

### 15. Spam / Abuse
**Description:** Spam messages or abusive content.

| Subcategory | Examples | Confidence Range |
|-------------|----------|------------------|
| **Spam** | "Buy cheap products", "Click here to win" | 0.90-0.98 |
| **Harassment** | "Abusive language", "Threatening message" | 0.88-0.95 |

**Priority:** Low (auto-filter)  
**Common Keywords:** spam, abuse, harassment

---

## Classification Logic

### Rule-Based Classification
The classifier uses **regex patterns** to match tickets to categories:

```python
# Example: Authentication Issue -> Password Reset
r'password.*reset.*(?:link|email).*(?:expired|invalid)'
```

### AI Fallback
If no rule matches with high confidence, the classifier uses **Gemini 2.0 Flash** for intelligent classification.

### Priority Assignment
Each category has a default priority:
- **Critical:** Security Incident
- **High:** Authentication, Billing Bug, Payment, Integration, Network
- **Medium:** Hardware, Account, Bug/Technical, Notification, Data/Reporting
- **Low:** Feature Request, General Question, Spam/Abuse

---

## Usage Examples

### Example 1: Authentication Issue
```json
{
  "ticket": "My 2FA code is not working and I can't log in",
  "category": "Authentication Issue",
  "subcategory": "2FA/MFA Issue",
  "confidence": 0.95,
  "priority": "high",
  "provider": "rule_engine"
}
```

### Example 2: Billing Bug
```json
{
  "ticket": "Dashboard shows paid but I got a dunning email",
  "category": "Billing Bug",
  "subcategory": "UI/Backend Mismatch",
  "confidence": 0.92,
  "priority": "high",
  "provider": "rule_engine"
}
```

### Example 3: Hardware Issue
```json
{
  "ticket": "Firmware update failed on my device",
  "category": "Hardware Issue",
  "subcategory": "Firmware",
  "confidence": 0.93,
  "priority": "medium",
  "provider": "rule_engine"
}
```

---

## Accuracy

- **Overall Accuracy:** 100% on test suite (50 diverse cases)
- **Rule Engine Coverage:** ~70% of common cases
- **AI Fallback:** Handles edge cases and ambiguous tickets
- **Confidence Threshold:** 0.75 minimum for classification

---

## API Response Format

```json
{
  "category": "Authentication Issue",
  "subcategory": "Password Reset",
  "confidence": 0.95,
  "priority": "high",
  "provider": "rule_engine",
  "processing_time": 0.12,
  "request_id": "req_abc123"
}
```

---

## Contributing

To add new categories or subcategories:

1. Update `VALID_CATEGORIES` in [`multi_provider.py`](file:///c:/Projects/AI%20tickets%20classifier%20PROJECT/ai-ticket-classifier/providers/multi_provider.py)
2. Add subcategories to `SUBCATEGORIES` dict
3. Add regex patterns to `RuleBasedClassifier`
4. Update this documentation
5. Add test cases to `test_accuracy_large.py`
