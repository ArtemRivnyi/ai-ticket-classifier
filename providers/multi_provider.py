"""
Multi-Provider System for AI Classification
Supports Gemini as primary and OpenAI as fallback
"""

import os
import logging
import re
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

VALID_CATEGORIES = [
    'Account Problem',
    'Authentication Issue',
    'Billing Bug',
    'Bug/Technical Issue',
    'Data / Reporting Issue',
    'Feature Request',
    'General Question',
    'Hardware Issue',
    'Integration Issue',
    'Mixed Issue',
    'Network Issue',
    'Notification Issue',
    'Payment Issue',
    'Security Incident',
    'Spam / Abuse',
    'Other'
]

SUBCATEGORIES = {
    'Authentication Issue': ['Login Failure', '2FA/MFA Issue', 'Password Reset', 'Session Expired'],
    'Hardware Issue': ['Device Malfunction', 'Battery/Power', 'Connectivity (Hardware)', 'Firmware'],
    'Billing Bug': ['Invoice Mismatch', 'UI/Backend Mismatch', 'Webhook Failure'],
    'Integration Issue': ['API Failure', 'Webhook Error', 'SSO/OAuth', 'Third-party Service'],
    'Notification Issue': ['Email Delivery', 'Slack/SMS', 'Partial Delivery'],
    'Payment Issue': ['Transaction Failed', 'Refund Request', 'Unrecognized Charge', 'Double Charge'],
    'Network Issue': ['Connectivity Loss', 'Latency/Slowness', 'VPN Issue', 'WiFi'],
    'Account Problem': ['Profile Update', 'Settings', 'Permissions'],
    'Bug/Technical Issue': ['Crash/Error', 'Performance', 'UI/UX Glitch'],
    'Security Incident': ['Unauthorized Access', 'Data Breach', 'Phishing'],
    'Feature Request': ['New Feature', 'Improvement', 'Configuration Change'],
    'General Question': ['How-to', 'Documentation', 'Pricing/Sales'],
    'Spam / Abuse': ['Spam', 'Harassment'],
    'Mixed Issue': ['Multiple Issues'],
    'Other': ['Unclassified']
}

CATEGORY_SYNONYMS = {
    'network': 'Network Issue',
    'vpn issue': 'Network Issue',
    'connectivity': 'Network Issue',
    'latency': 'Network Issue',
    'outage': 'Network Issue',
    'wifi': 'Network Issue',
    'account': 'Account Problem',
    'profile': 'Account Problem',
    'settings': 'Account Problem',
    'login': 'Authentication Issue',
    'password': 'Authentication Issue',
    '2fa': 'Authentication Issue',
    'otp': 'Authentication Issue',
    'verification': 'Authentication Issue',
    'mfa': 'Authentication Issue',
    'billing': 'Payment Issue',
    'payment': 'Payment Issue',
    'charge': 'Payment Issue',
    'charged': 'Payment Issue',
    'refund': 'Payment Issue',
    'invoice': 'Payment Issue',
    'invoice mismatch': 'Billing Bug',
    'billing bug': 'Billing Bug',
    'ui payment': 'Billing Bug',
    'processor mismatch': 'Billing Bug',
    'idea': 'Feature Request',
    'suggestion': 'Feature Request',
    'roadmap': 'Feature Request',
    'bug': 'Bug/Technical Issue',
    'crash': 'Bug/Technical Issue',
    'error': 'Bug/Technical Issue',
    'exception': 'Bug/Technical Issue',
    'hardware': 'Hardware Issue',
    'printer': 'Hardware Issue',
    'camera': 'Hardware Issue',
    'sensor': 'Hardware Issue',
    'battery': 'Hardware Issue',
    'card reader': 'Hardware Issue',
    'api': 'Integration Issue',
    'webhook': 'Integration Issue',
    'integration': 'Integration Issue',
    'sdk': 'Integration Issue',
    'oauth': 'Integration Issue',
    'sso': 'Integration Issue',
    'slack': 'Notification Issue',
    'notification': 'Notification Issue',
    'email': 'Notification Issue',
    'sms': 'Notification Issue',
    'alert': 'Notification Issue',
    'security': 'Security Incident',
    'breach': 'Security Incident',
    'hacked': 'Security Incident',
    'ransomware': 'Security Incident',
    'compromised': 'Security Incident',
    'phishing': 'Security Incident',
    'report': 'Data / Reporting Issue',
    'analytics': 'Data / Reporting Issue',
    'analytics': 'Data / Reporting Issue',
    'integration / api issue': 'Integration Issue'
}

PRIORITY_MAP = {
    'Security Incident': 'critical',
    'Network Issue': 'high',
    'Billing Bug': 'high',
    'Payment Issue': 'high',
    'Authentication Issue': 'high',
    'Hardware Issue': 'medium',
    'Integration Issue': 'medium',
    'Bug/Technical Issue': 'medium',
    'Account Problem': 'medium',
    'Data / Reporting Issue': 'medium',
    'Notification Issue': 'medium',
    'Mixed Issue': 'medium',
    'Spam / Abuse': 'low',
    'Feature Request': 'low',
    'General Question': 'low',
    'Other': 'medium'
}

# CRITICAL priority keywords
CRITICAL_KEYWORDS = [
    r'production down',
    r'server down',
    r'all users affected',
    r'can\'t work',
    r'losing money',
    r'complete outage',
    r'system crash',
    r'data loss'
]

BLACKLIST_KEYWORDS = [
    r'free money',
    r'visit .*bitcoin',
    r'click here',
    r'phishing',
    r'buy now'
]



# Precedence order for resolving multiple matches
# Specific/Critical categories > Generic categories
CATEGORY_PRECEDENCE = [
    'Security Incident',
    'Billing Bug',
    'Hardware Issue',
    'Integration Issue',  # Swapped back to prioritize over Notification Issue
    'Notification Issue',
    'Authentication Issue',
    'Payment Issue',
    'Account Problem',
    'Network Issue',
    'Bug/Technical Issue',
    'Data / Reporting Issue',
    'Feature Request',
    'General Question',
    'Spam / Abuse',
    'Mixed Issue',
    'Other'
]

def _compile_category_rules() -> List[Dict]:
    return [
        {
            'category': 'Billing Bug',
            'subcategory': 'Invoice Mismatch',
            'patterns': [
                r'invoice (mismatch|says)',
                r'invoice.*\$\d+.*charged.*\$\d+',
                r'charged twice.*invoice',
                r'same invoice.*twice',
                r'tax.*wrong',
                r'tax.*calculation',
            ],
        },
        {
            'category': 'Billing Bug',
            'subcategory': 'Webhook Failure',
            'patterns': [
                r'processor (did not confirm|charged)',
                r'webhook (shows|mismatch)',
                r'stripe.*failed',
            ],
        },
        {
            'category': 'Billing Bug',
            'subcategory': 'UI/Backend Mismatch',
            'patterns': [
                r'dashboard.*paid.*dunning',
                r'says.*paid.*dunning',
                r'ui shows paid',
                r'logs show unpaid',
                r'dashboard shows paid.*backend',
                r'backend.*unpaid',
                r'status.*active.*features.*locked',
                r'subscription.*active.*locked',
            ],
        },
        {
            'category': 'Feature Request',
            'subcategory': 'New Feature',
            'patterns': [
                r'add animation',
                r'feature request',
                r'new feature',
                r'need an api',
                r'create an api',
                r'\badd dark mode',
                r'\badd.*dark mode',
            ],
        },
        {
            'category': 'Feature Request',
            'subcategory': 'Improvement',
            'patterns': [
                r'would be nice',
                r'nice to have',
                r'would like',
                r'suggestion',
                r'improvement',
                r'enhancement',
                r'can you add',
                r'make the.*collapsible',
                r'export to',
            ],
        },
        {
            'category': 'Hardware Issue',
            'subcategory': 'Battery/Power',
            'patterns': [
                r'\bbattery\b',
                r'\bac\b',
                r'drains in',
            ],
        },
        # Firmware MUST come before Device Malfunction to catch "device firmware update failed"
        {
            'category': 'Hardware Issue',
            'subcategory': 'Firmware',
            'patterns': [
                r'firmware.*update.*failed',
                r'firmware.*failed',
                r'firmware update',
            ],
        },
        {
            'category': 'Hardware Issue',
            'subcategory': 'Device Malfunction',
            'patterns': [
                r'\bcamera\b',
                r'\bsensor\b',
                r'\bprinter\b',
                r'card reader',
                r'\bdevice\b',
                r'jamming',
                r'not detecting',
                r'stopped working',
            ],
        },
        {
            'category': 'Hardware Issue',
            'subcategory': 'Connectivity (Hardware)',
            'patterns': [
                r'\brouter\b',
            ],
        },
        {
            'category': 'Integration Issue',
            'subcategory': 'Webhook Error',
            'patterns': [
                r'webhook',
                r'callback',
            ],
        },
        {
            'category': 'Integration Issue',
            'subcategory': 'API Failure',
            'patterns': [
                r'api.*error',
                r'api.*fail',
                r'api.*timeout',
                r'\bsdk\b',
                r'api.*not responding',
            ],
        },
        # Authentication Login Failure MUST come before SSO/OAuth to catch "sso login button"
        {
            'category': 'Authentication Issue',
            'subcategory': 'Login Failure',
            'patterns': [
                r'cannot log in',
                r"can't log in",
                r'failed login',
                r'login button.*greyed',
                r'locked out',
                r'sso.*button',
                r'sso.*login.*button',
            ],
        },
        {
            'category': 'Integration Issue',
            'subcategory': 'SSO/OAuth',
            'patterns': [
                r'auth token',
                r'azure ad',
                r'oauth',
                r'invalid_grant',
            ],
        },
        {
            'category': 'Integration Issue',
            'subcategory': 'Third-party Service',
            'patterns': [
                r'integration',
                r'slack.*not coming',
                r'slack.*notifications',
                r'salesforce',
                r'hubspot',
                r'jira',
            ],
        },
        {
            'category': 'Notification Issue',
            'subcategory': 'Email Delivery',
            'patterns': [
                r'email.*not delivered',
                r'didn\'t receive.*email',
                r'email.*spam',
                r'email.*blank',
            ],
        },
        {
            'category': 'Notification Issue',
            'subcategory': 'Partial Delivery',
            'patterns': [
                r'half.*team',
                r'some users',
                r'partial.*delivery',
                r'delayed.*hours',
                r'notifications.*delayed',
                r'notifications.*some',
            ],
        },
        {
            'category': 'Notification Issue',
            'subcategory': 'Slack/SMS',
            'patterns': [
                r'slack.*alerts',
                r'\bsms\b',
                r'\balert\b',
                r'push message',
            ],
        },
        {
            'category': 'Notification Issue',
            'subcategory': None, # General
            'patterns': [
                r'notification',
            ],
        },
        {
            'category': 'Authentication Issue',
            'subcategory': '2FA/MFA Issue',
            'patterns': [
                r'invalid code',
                r'verification (code|failed)',
                r'\b2fa\b',
                r'\bmfa\b',
                r'\botp\b',
                r'verification code',
                r'authenticator',
            ],
        },
        {
            'category': 'Authentication Issue',
            'subcategory': 'Login Failure',
            'patterns': [
                r'cannot log in',
                r"can't log in",
                r'failed login',
                r'login button.*greyed',
                r'locked out',
                r'sso.*button',
            ],
        },
        {
            'category': 'Authentication Issue',
            'subcategory': 'Session Expired',
            'patterns': [
                r'session expired',
                r'session timeout',
                r'logged out',
            ],
        },
        {
            'category': 'Authentication Issue',
            'subcategory': 'Password Reset',
            'patterns': [
                r'reset link',
                r'password reset',
                r'forgot.*password',
            ],
        },
        {
            'category': 'Payment Issue',
            'subcategory': 'Double Charge',
            'patterns': [
                r'charged twice',
                r'double charge',
                r'duplicate charge',
                r'billed twice',
                r'same invoice.*twice',
            ],
        },
        {
            'category': 'Payment Issue',
            'subcategory': 'Refund Request',
            'patterns': [
                r'refund',
                r'chargeback',
            ],
        },
        {
            'category': 'Payment Issue',
            'subcategory': 'Transaction Failed',
            'patterns': [
                r'transaction failed',
                r'payment failed',
                r'payment completed', # Context usually implies issue despite "completed"
                r'insufficient funds',
                r'card expired',
                r'payment.*error',
                r'transaction.*error',
                r'credit card.*expired',
            ],
        },
        {
            'category': 'Payment Issue',
            'subcategory': 'Unrecognized Charge',
            'patterns': [
                r'\bcharged\b',
                r'unauthorized payment',
                r'invoice',
                r'billing',
                r'don\'t recognize',
                r'unknown charge',
            ],
        },
        {
            'category': 'Security Incident',
            'subcategory': 'Data Breach',
            'patterns': [
                r'breach',
                r'data leak',
            ],
        },
        {
            'category': 'Security Incident',
            'subcategory': 'Unauthorized Access',
            'patterns': [
                r'hacked',
                r'compromised',
                r'intrusion',
            ],
        },
        {
            'category': 'Bug/Technical Issue',
            'subcategory': 'Performance',
            'patterns': [
                r'slow',
                r'takes.*seconds',
                r'loading',
                r'latency',
            ],
        },
        {
            'category': 'Bug/Technical Issue',
            'subcategory': 'UI/UX Glitch',
            'patterns': [
                r'misaligned',
                r'glitch',
                r'overlap',
                r'css',
                r'style',
            ],
        },
        {
            'category': 'Bug/Technical Issue',
            'subcategory': 'Crash/Error',
            'patterns': [
                r'crash',
                r'error',
                r'exception',
                r'traceback',
                r'undefined',
                r'not a function',
                r'empty', # Search results empty
            ],
        },
        {
            'category': 'Bug/Technical Issue',
            'subcategory': 'Crash/Error',
            'patterns': [
                r'null pointer',
                r'javascript error',
                r'stacktrace',
                r'crash when',
                r'error',
                r'crash',
                r'bug',
            ],
        },
        {
            'category': 'Bug/Technical Issue',
            'subcategory': 'UI/UX Glitch',
            'patterns': [
                r'cosmetic issue',
                r'button alignment',
                r'minor (issue|bug)',
            ],
        },
        {
            'category': 'Network Issue',
            'subcategory': 'Connectivity Loss',
            'patterns': [
                r'cannot connect',
                r'connection timeout',
                r'\binternet\b',
                r'packet loss',
            ],
        },
        {
            'category': 'Network Issue',
            'subcategory': 'VPN Issue',
            'patterns': [
                r'\bvpn\b',
            ],
        },
        {
            'category': 'Network Issue',
            'subcategory': 'WiFi',
            'patterns': [
                r'\bwifi\b',
            ],
        },
        {
            'category': 'Network Issue',
            'subcategory': 'Latency/Slowness',
            'patterns': [
                r'latency',
                r'\bnetwork\b',
                r'connectivity',
            ],
        },
        {
            'category': 'Account Problem',
            'subcategory': 'Profile Update',
            'patterns': [
                r'profile update',
                r'wrong email',
            ],
        },
        {
            'category': 'Account Problem',
            'subcategory': 'Profile Update',
            'patterns': [
                r'change.*email',
                r'wrong name',
                r'update.*profile',
            ],
        },
        {
            'category': 'Account Problem',
            'subcategory': 'Settings',
            'patterns': [
                r'account settings',
                r'delete my account',
                r'upgrade.*plan',
            ],
        },
        {
            'category': 'Account Problem',
            'subcategory': 'Permissions',
            'patterns': [
                r'access.*page',
                r'permission',
                r'admin access',
            ],
        },
        {
            'category': 'Account Problem',
            'subcategory': None,
            'patterns': [
                r'phishing', # Context dependent, but kept from original
                r'crypto',
                r'promo',
            ],
        },
        {
            'category': 'General Question',
            'subcategory': 'How-to',
            'patterns': [
                r'how do i',
                r'can you explain',
            ],
        },
        {
            'category': 'General Question',
            'subcategory': None,
            'patterns': [
                r'general question',
            ],
        },
        {
            'category': 'Mixed Issue',
            'subcategory': 'Multiple Issues',
            'patterns': [
                r'\bAND\b.*failed',
                r'two (separate|different) (issues|problems)',
                r'multiple (issues|problems)',
                r'both.*and',
            ],
        },
    ]

class RuleBasedClassifier:
    """Deterministic regex/keyword rules for obvious cases."""

    def __init__(self):
        self.rules = _compile_category_rules()

    def classify(self, ticket_text: str) -> Optional[Dict]:
        text = ticket_text.lower()
        matches = []
        
        # Debug logging
        logger.info(f"🔍 Rule Engine processing: '{text[:50]}...'")
        
        # Find all matching categories
        for i, rule in enumerate(self.rules):
            if any(re.search(pattern, text) for pattern in rule['patterns']):
                matches.append({
                    'index': i,
                    'category': rule['category'],
                    'subcategory': rule.get('subcategory')
                })
                logger.info(f"✅ Match found: {rule['category']} -> {rule.get('subcategory')}")
        
        if not matches:
            logger.info("❌ No rules matched")
            return None

        # Special case: If Mixed Issue explicit pattern matches, it takes precedence
        mixed_match = next((m for m in matches if m['category'] == 'Mixed Issue'), None)
        if mixed_match:
            return {
                'category': 'Mixed Issue',
                'subcategory': mixed_match['subcategory'] or 'Multiple Issues',
                'confidence': 0.85,
                'priority': 'high',
                'provider': 'rule_engine'
            }

        # Select the best category based on precedence
        # Sort by:
        # 1. Category Precedence (lower index = higher priority)
        # 2. Rule Index (lower index = more specific rule, assuming rules are ordered)
        
        def sort_key(match):
            try:
                cat_priority = CATEGORY_PRECEDENCE.index(match['category'])
            except ValueError:
                cat_priority = float('inf')
            return (cat_priority, match['index'])

        matches.sort(key=sort_key)
        best_match = matches[0]

        return {
            'category': best_match['category'],
            'subcategory': best_match['subcategory'],
            'confidence': 0.85,  # High confidence for rule matches
            'priority': PRIORITY_MAP.get(best_match['category'], 'medium'),
            'provider': 'rule_engine'
        }


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Simple circuit breaker for provider failover"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Reset on successful call"""
        self.failures = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Increment failures and open circuit if threshold reached"""
        self.failures += 1
        self.last_failure_time = datetime.now()
        
        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failures} failures")
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        
        return (datetime.now() - self.last_failure_time).total_seconds() >= self.timeout


class MultiProvider:
    def __init__(self):
        self.gemini_available = False
        self.openai_available = False
        self.allow_providerless = os.getenv("ALLOW_PROVIDERLESS", "false").lower() == "true"
        self.gemini_circuit = CircuitBreaker()
        self.openai_circuit = CircuitBreaker()
        self.rule_classifier = RuleBasedClassifier()
        
        # Initialize Gemini
        try:
            import google.generativeai as genai
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                logger.warning("⚠️ GEMINI_API_KEY not found")
            else:
                try:
                    genai.configure(api_key=api_key)
                    # Try different models in order of preference
                    models_to_try = [
                        'gemini-2.0-flash-exp',
                        'gemini-2.0-flash',
                        'gemini-1.5-pro',
                        'gemini-1.5-flash',
                        'gemini-pro'
                    ]
                    
                    model_initialized = False
                    for model_name in models_to_try:
                        try:
                            self.gemini_model = genai.GenerativeModel(model_name)
                            self.gemini_available = True
                            logger.info(f"✅ Gemini provider initialized with {model_name}")
                            model_initialized = True
                            break
                        except Exception as model_error:
                            logger.debug(f"Failed to initialize {model_name}: {model_error}")
                            continue
                    
                    if not model_initialized:
                        raise Exception("Could not initialize any Gemini model")
                        
                except Exception as config_error:
                    error_str = str(config_error).lower()
                    if 'metaclass' in error_str or 'tp_new' in error_str:
                        # Python version compatibility issue - try to work around
                        logger.warning(f"⚠️ Gemini provider has Python version compatibility issue: {config_error}")
                        logger.warning("⚠️ Trying alternative initialization...")
                        try:
                            # Try simpler model initialization
                            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                            self.gemini_available = True
                            logger.info("✅ Gemini provider initialized (workaround applied)")
                        except:
                            logger.error(f"❌ Gemini provider failed even with workaround: {config_error}")
                    else:
                        raise
        except ImportError as import_error:
            logger.warning(f"⚠️ google-generativeai not available: {import_error}")
        except Exception as e:
            logger.warning(f"⚠️ Gemini provider failed: {e}")
        
        # Initialize OpenAI (optional fallback)
        try:
            from openai import OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
                self.openai_available = True
                logger.info("✅ OpenAI provider initialized")
        except Exception as e:
            logger.info(f"ℹ️ OpenAI not configured (optional): {e}")
        
        # Don't raise error if no providers - allow app to start and return 503 on requests
        if not self.gemini_available and not self.openai_available:
            if self.allow_providerless:
                logger.warning("⚠️ No AI providers available. Running in rule-only mode (ALLOW_PROVIDERLESS=true)")
            else:
                logger.warning("⚠️ No AI providers available. Please set GEMINI_API_KEY or OPENAI_API_KEY")
                logger.warning("⚠️ Application will start but classification endpoints will return 503")
        else:
            logger.info(f"🚀 MultiProvider initialized (Gemini: {self.gemini_available}, OpenAI: {self.openai_available})")
    
    def classify(self, ticket_text: str) -> Dict:
        """Classify ticket using Rule Engine first, then AI"""
        
        # 1. Try Rule Engine FIRST (Deterministic & Fast)
        # We prioritize rules because they are now highly specific and accurate
        rule_match = self.rule_classifier.classify(ticket_text)
        if rule_match:
            logger.info(f"✅ Rule Engine matched: {rule_match['category']}")
            return self._post_process_result(rule_match, ticket_text)

        # Check if any provider is available for fallback
        if not self.gemini_available and not self.openai_available and not self.allow_providerless:
            raise Exception("No AI providers available. Please set GEMINI_API_KEY or OPENAI_API_KEY")
        
        prompt = f"""
You are an AI assistant that classifies support tickets into EXACTLY one of the approved categories and subcategories.

IMPORTANT CONTEXT:
- If ticket mentions "crash" or "bug" or "error", it's Bug/Technical Issue (not Payment/Account)
- If ticket mentions "production/server down" + "multiple users", Priority = CRITICAL
- Look at PRIMARY issue, not secondary keywords
- If it's a simple question ("how to", "what is"), it's General Question

Allowed Categories and Subcategories:
{chr(10).join([f"{k}: {', '.join(v)}" for k, v in SUBCATEGORIES.items()])}

Examples:
- "VPN is down for the whole office" → Category: Network Issue, Subcategory: VPN Issue
- "Please refund the duplicate charge from yesterday" → Category: Payment Issue, Subcategory: Refund Request
- "I need to reset my password again" → Category: Authentication Issue, Subcategory: Password Reset
- "Could you add dark mode to the dashboard?" → Category: Feature Request, Subcategory: New Feature
- "App crashes when I upload files" → Category: Bug/Technical Issue, Subcategory: Crash/Error
- "How do I export my data?" → Category: General Question, Subcategory: How-to
- "Click here to claim free crypto" → Category: Spam / Abuse, Subcategory: Spam

Ticket: {ticket_text}

Respond with a JSON object containing 'category' and 'subcategory'. Example:
{{"category": "Network Issue", "subcategory": "VPN Issue"}}"""

        # 2. Try AI (Gemini/OpenAI) if rules failed
        
        ai_result = None
        
        # Try Gemini first
        if self.gemini_available:
            try:
                def classify_with_gemini():
                    import json
                    response = self.gemini_model.generate_content(prompt)
                    text = response.text.strip()
                    # Try to parse JSON
                    try:
                        # Clean up markdown code blocks if present
                        if text.startswith("```json"):
                            text = text[7:-3]
                        elif text.startswith("```"):
                            text = text[3:-3]
                        
                        data = json.loads(text)
                        category = data.get('category', 'Other')
                        subcategory = data.get('subcategory')
                    except json.JSONDecodeError:
                        # Fallback if not JSON (legacy behavior or model error)
                        category = text
                        subcategory = None
                        
                    return {
                        'category': category,
                        'subcategory': subcategory,
                        'confidence': 0.95,
                        'provider': 'gemini'
                    }
                
                ai_result = self.gemini_circuit.call(classify_with_gemini)
                
            except Exception as e:
                logger.error(f"Gemini classification failed: {e}")
                if not self.openai_available:
                    raise
        
        # Fallback to OpenAI if Gemini fails
        if not ai_result and self.openai_available:
            try:
                def classify_with_openai():
                    import json
                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a ticket classification system. Respond with JSON object containing 'category' and 'subcategory'."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=100,
                        temperature=0.3
                    )
                    text = response.choices[0].message.content.strip()
                    try:
                         data = json.loads(text)
                         category = data.get('category', 'Other')
                         subcategory = data.get('subcategory')
                    except json.JSONDecodeError:
                        category = text
                        subcategory = None

                    return {
                        'category': category,
                        'subcategory': subcategory,
                        'confidence': 0.90,
                        'provider': 'openai'
                    }
                
                ai_result = self.openai_circuit.call(classify_with_openai)
                
            except Exception as e:
                logger.error(f"OpenAI classification failed: {e}")
                raise
        
        # Use AI result
        if ai_result:
            return self._post_process_result(ai_result, ticket_text)
        
        # If we get here, all providers failed or unavailable
        if self.allow_providerless:
            logger.info("Rule-only mode: returning fallback classification")
            fallback_result = {
                'category': 'Other',
                'subcategory': 'Unclassified',
                'confidence': 0.5,
                'provider': 'rule_engine'
            }
            return self._post_process_result(fallback_result, ticket_text)
        raise Exception("All providers failed")
    
    def _post_process_result(self, result: Dict, ticket_text: str) -> Dict:
        """Normalize category names and apply blacklist corrections"""
        category = result.get('category', 'Other')
        normalized = self._normalize_category(category)

        if self._matches_blacklist(ticket_text):
            normalized = 'Spam / Abuse'

        if normalized not in VALID_CATEGORIES:
            normalized = 'Other'

        result['category'] = normalized
        
        # Validate subcategory
        subcategory = result.get('subcategory')
        if normalized in SUBCATEGORIES:
            valid_subs = SUBCATEGORIES[normalized]
            if subcategory not in valid_subs:
                # Try to find a matching subcategory or default to first/None
                result['subcategory'] = None
        else:
            result['subcategory'] = None
        
        # Determine priority
        priority = PRIORITY_MAP.get(normalized, 'medium')
        
        # Check for CRITICAL keywords
        if self._is_critical(ticket_text):
            priority = 'critical'
            
        # Check for LOW priority keywords
        if self._is_low_priority(ticket_text):
            priority = 'low'
        
        result['priority'] = priority
        
        if 'confidence' not in result or result['confidence'] is None:
            result['confidence'] = 0.75
        return result

    def _normalize_category(self, category: Optional[str]) -> str:
        if not category:
            return 'Other'
        cleaned = category.strip()
        key = cleaned.lower()
        if key in CATEGORY_SYNONYMS:
            return CATEGORY_SYNONYMS[key]
        # Try partial matches
        for synonym, canonical in CATEGORY_SYNONYMS.items():
            if synonym in key:
                return canonical
        if cleaned in VALID_CATEGORIES:
            return cleaned
        return cleaned.title()

    def _is_critical(self, ticket_text: str) -> bool:
        """Check if ticket should be marked as CRITICAL priority"""
        text = ticket_text.lower()
        return any(re.search(pattern, text) for pattern in CRITICAL_KEYWORDS)

    def _is_low_priority(self, ticket_text: str) -> bool:
        """Check if ticket should be marked as LOW priority"""
        text = ticket_text.lower()
        low_keywords = [
            r'cosmetic', r'typo', r'color', r'alignment', r'spacing',
            r'minor', r'not\s+urgent', r'nice\s+to\s+have', r'suggestion'
        ]
        return any(re.search(pattern, text) for pattern in low_keywords)

    def _determine_priority(self, category: Optional[str]) -> str:
        """Backward-compatible priority helper used in tests."""
        normalized = self._normalize_category(category or 'Other')
        return PRIORITY_MAP.get(normalized, 'medium')

    def _matches_blacklist(self, ticket_text: str) -> bool:
        text = ticket_text.lower()
        return any(re.search(pattern, text) for pattern in BLACKLIST_KEYWORDS)
    
    def get_status(self) -> Dict:
        """Get provider availability status"""
        return {
            'gemini': 'available' if self.gemini_available else 'unavailable',
            'openai': 'available' if self.openai_available else 'unavailable'
        }


# Alias for backward compatibility
class MultiProviderClassifier(MultiProvider):
    """
    Wrapper class for backward compatibility
    The app.py expects MultiProviderClassifier, so we provide it as an alias
    """
    pass
