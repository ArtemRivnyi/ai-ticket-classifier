# Release Notes

## v2.5.0 - Enhanced AI Prompt with Few-Shot Learning (2025-11-20)

### 🚀 New Features

#### 🧠 Enhanced Gemini Prompt
- **15 Few-Shot Examples** covering all major subcategories and edge cases
- **Strict Classification Rules** to prevent hallucination
- **Pattern Hints** for tricky cases (SSO, webhooks, 2FA, billing bugs)
- **JSON Response Format** for consistent parsing
- **Gemini 2.0 Flash** for improved performance

#### 📚 Comprehensive Examples
Examples cover:
- Authentication: 2FA/MFA, Password Reset, Session Expired
- Integration: SSO/OAuth, Webhook Error, API Failure
- Billing: Invoice Mismatch, UI/Backend Mismatch
- Payment: Transaction Failed, Double Charge
- Network: Connectivity Loss
- Hardware: Firmware issues
- Security: Unauthorized Access
- Performance: Slow/Laggy apps

### 🛠️ Improvements
- Better handling of ambiguous tickets
- Reduced false positives on edge cases
- Improved subcategory accuracy
- More consistent confidence scores

### 📦 Technical Changes
- Updated `providers/gemini_provider.py` with comprehensive prompt
- Added JSON parsing with fallback handling
- Improved error logging for classification failures

---

## v2.4.0 - Analytics & Feedback (2025-11-20)

### 🚀 New Features

#### 📊 Analytics & Monitoring
- **5 New Prometheus Metrics** for real-time classification insights:
  - `classification_confidence_score` - Histogram of confidence distributions
  - `category_classifications_total` - Category usage counter
  - `subcategory_classifications_total` - Subcategory usage counter
  - `provider_usage_total` - Rule engine vs AI provider usage
  - `classification_errors_total` - Error tracking by type
- Metrics automatically recorded on every classification
- Available at `/metrics` endpoint for Prometheus/Grafana

#### 💬 User Feedback System
- **3 New API Endpoints** for collecting classification quality feedback:
  - `POST /api/v1/feedback` - Submit feedback (correct/incorrect)
  - `GET /api/v1/feedback/stats` - Get real-time accuracy statistics
  - `GET /api/v1/feedback/<request_id>` - Get specific feedback
- No authentication required for feedback submission
- Real-time accuracy tracking from user feedback

### 🛠️ Improvements
- Enhanced monitoring capabilities for production insights
- Better visibility into classification performance
- Foundation for continuous improvement based on user feedback

### 📦 API Changes
- **New endpoints**: `/api/v1/feedback/*`
- **New metrics**: Available at `/metrics`
- **No breaking changes** - fully backward compatible

---

## v2.3.0 - 100% Accuracy Achievement (2025-11-20)

### 🚀 New Features

#### 🧠 Granular Subcategories
- Implemented 2-level classification system (Category → Subcategory)
- Added support for **50+ subcategories** across 15 main categories
- Examples:
    - `Authentication Issue` → `2FA/MFA Issue`, `Session Expired`
    - `Billing Bug` → `Invoice Mismatch`, `Webhook Failure`
    - `Hardware Issue` → `Device Malfunction`, `Firmware`

#### 🧹 Smart Text Cleaning
- Added `clean_text` pre-processor to remove:
    - Email signatures ("Sent from my iPhone", etc.)
    - Forwarded message headers
    - Excessive whitespace and noise
- Improves AI accuracy by focusing on core issues

#### 🛡️ Enhanced Rule Engine
- Refined regex patterns for higher precision
- Implemented strict rule precedence (Specific > General)
- Added fallback rules for critical paths (SSO, Password Reset)

### 🛠️ Improvements
- **Accuracy**: Achieved **100% accuracy** on comprehensive test suite (50 diverse edge cases)
- **Resilience**: Enabled `ALLOW_PROVIDERLESS` mode by default
- **Testing**: Added `test_accuracy_large.py` with rate limit protection

### 📦 API Changes
- **Response Format**: Now includes `subcategory` field
```json
{
  "category": "Authentication Issue",
  "subcategory": "Password Reset",
  "confidence": 0.95,
  "provider": "rule_engine"
}
```
