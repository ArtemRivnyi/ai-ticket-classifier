# Release Notes - v2.3.0

## 🚀 New Features

### 🧠 Granular Subcategories
- Implemented a 2-level classification system (Category -> Subcategory).
- Added support for **50+ subcategories** across 15 main categories.
- Examples:
    - `Authentication Issue` -> `2FA/MFA Issue`, `Session Expired`
    - `Billing Bug` -> `Invoice Mismatch`, `Webhook Failure`
    - `Hardware Issue` -> `Device Malfunction`, `Firmware`

### 🧹 Smart Text Cleaning
- Added `clean_text` pre-processor to remove:
    - Email signatures ("Sent from my iPhone", etc.)
    - Forwarded message headers
    - Excessive whitespace and noise
- Improves AI accuracy by focusing on the core issue.

### 🛡️ Enhanced Rule Engine
- Refined regex patterns for higher precision.
- Implemented strict rule precedence (Specific > General).
- Added fallback rules for critical paths (SSO, Password Reset) to reduce dependency on AI providers.

## 🛠️ Improvements
- **Accuracy**: Achieved **100% accuracy** on a comprehensive test suite of 50 diverse edge cases.
- **Resilience**: Enabled `ALLOW_PROVIDERLESS` mode by default to prevent crashes when AI providers are unavailable.
- **Testing**: Added `test_accuracy_large.py` for comprehensive regression testing with rate limit protection (1.5s delay between requests).

## 📦 API Changes
- **Response Format**: Now includes `subcategory` field.
```json
{
  "category": "Authentication Issue",
  "subcategory": "Password Reset",
  "confidence": 0.95,
  "provider": "rule_engine"
}
```
