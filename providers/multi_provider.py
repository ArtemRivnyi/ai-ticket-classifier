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
    'dashboard': 'Data / Reporting Issue',
    'export': 'Data / Reporting Issue',
    'metrics': 'Data / Reporting Issue',
    'question': 'General Question',
    'how to': 'General Question',
    'faq': 'General Question',
    'spam': 'Spam / Abuse',
    'abuse': 'Spam / Abuse',
    'promotion': 'Spam / Abuse',
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
            'patterns': [
                r'ui shows paid',
                r'logs show unpaid',
                r'invoice (mismatch|says)',
                r'processor (did not confirm|charged)',
                r'webhook (shows|mismatch)',
                r'dashboard shows paid.*backend',
                r'backend.*unpaid',
                r'stripe.*failed',
                r'invoice.*\$\d+.*charged.*\$\d+',
            ],
        },
        {
            'category': 'Hardware Issue',
            'patterns': [
                r'\bcamera\b',
                r'\bsensor\b',
                r'\bprinter\b',
                r'card reader',
                r'\brouter\b',
                r'\bbattery\b',
                r'\bdevice\b',
                r'\bac\b',
                r'firmware update',
                r'drains in',
                r'jamming',
                r'not detecting',
                r'stopped working',
            ],
        },
        {
            'category': 'Integration Issue',
            'patterns': [
                r'\bapi\b',
                r'webhook',
                r'integration',
                r'\bsdk\b',
                r'callback',
                r'auth token',
                r'\bsso\b',
                r'azure ad',
                r'oauth',
                r'invalid_grant',
                r'api.*not responding',
                r'timeout',
                r'slack\s+integration',
            ],
        },
        {
            'category': 'Notification Issue',
            'patterns': [
                r'notification',
                r'email.*not delivered',
                r'slack.*alerts',
                r'\bsms\b',
                r'\balert\b',
                r'push message',
                r'half.*team',
                r'some users',
                r'partial.*delivery',
                r'notifications.*some',
            ],
        },
        {
            'category': 'Authentication Issue',
            'patterns': [
                r'cannot log in',
                r"can't log in",
                r'failed login',
                r'invalid code',
                r'verification (code|failed)',
                r'reset link expired',
                r'\b2fa\b',
                r'\bmfa\b',
                r'\botp\b',
                r'verification code',
                r'authenticator',
                r'password reset',
            ],
        },
        {
            'category': 'Payment Issue',
            'patterns': [
                r'payment failed',
                r'payment completed',
                r'\bcharged\b',
                r'charged twice',
                r'chargeback',
                r'refund',
                r'unauthorized payment',
                r'duplicate charge',
                r'invoice',
                r'billing',
            ],
        },
        {
            'category': 'Security Incident',
            'patterns': [
                r'security alert',
                r'breach',
                r'hacked',
                r'compromised',
                r'data leak',
                r'intrusion',
            ],
        },
        {
            'category': 'Bug/Technical Issue',
            'patterns': [
                r'null pointer',
                r'javascript error',
                r'stacktrace',
                r'crash when',
                r'cosmetic issue',
                r'button alignment',
                r'minor (issue|bug)',
                r'error',
                r'crash',
                r'bug',
            ],
        },
        {
            'category': 'Network Issue',
            'patterns': [
                r'\bvpn\b',
                r'\bnetwork\b',
                r'latency',
                r'packet loss',
                r'connectivity',
                r'connection timeout',
                r'cannot connect',
                r'\bwifi\b',
                r'\binternet\b',
            ],
        },
        {
            'category': 'Account Problem',
            'patterns': [
                r'profile update',
                r'account settings',
                r'wrong email',
                r'phishing',
                r'crypto',
                r'promo',
            ],
        },
        {
            'category': 'General Question',
            'patterns': [
                r'how do i',
                r'can you explain',
                r'general question',
            ],
        },
        {
            'category': 'Mixed Issue',
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
        matches = set()
        
        # Debug logging
        logger.info(f"🔍 Rule Engine processing: '{text[:50]}...'")
        
        # Find all matching categories
        for rule in self.rules:
            if any(re.search(pattern, text) for pattern in rule['patterns']):
                matches.add(rule['category'])
                logger.info(f"✅ Match found: {rule['category']}")
        
        if not matches:
            logger.info("❌ No rules matched")
            return None

        # Special case: If Mixed Issue explicit pattern matches, it takes precedence
        # This handles cases like "login AND payment failed"
        if 'Mixed Issue' in matches:
            return {
                'category': 'Mixed Issue',
                'confidence': 0.85,
                'priority': 'high',
                'provider': 'rule_engine'
            }

        # Select the best category based on precedence
        best_category = None
        best_index = float('inf')
        
        for category in matches:
            try:
                index = CATEGORY_PRECEDENCE.index(category)
                if index < best_index:
                    best_index = index
                    best_category = category
            except ValueError:
                continue
        
        if not best_category:
            # Fallback if category not in precedence list (shouldn't happen)
            best_category = list(matches)[0]

        return {
            'category': best_category,
            'confidence': 0.85,  # High confidence for rule matches
            'priority': PRIORITY_MAP.get(best_category, 'medium'),
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
        if not self.gemini_available and not self.openai_available:
            raise Exception("No AI providers available. Please set GEMINI_API_KEY or OPENAI_API_KEY")
        
        prompt = f"""
You are an AI assistant that classifies support tickets into EXACTLY one of the approved categories.

IMPORTANT CONTEXT:
- If ticket mentions "crash" or "bug" or "error", it's Bug/Technical Issue (not Payment/Account)
- If ticket mentions "production/server down" + "multiple users", Priority = CRITICAL
- Look at PRIMARY issue, not secondary keywords
- If it's a simple question ("how to", "what is"), it's General Question

Allowed categories (respond with one of them verbatim):
1. Network Issue — connectivity, VPN, latency, networking
2. Account Problem — login, password, user profile
3. Payment Issue — billing, charges, refunds, invoices
4. Feature Request — enhancements, suggestions, roadmap asks
5. Bug/Technical Issue — crashes, errors, bugs, technical problems
6. General Question — how-to questions, general inquiries
7. Spam / Abuse — phishing, unsolicited promos, abuse
8. Other — anything that does not match above

Examples:
- "VPN is down for the whole office" → Network Issue
- "Please refund the duplicate charge from yesterday" → Payment Issue
- "I need to reset my password again" → Account Problem
- "Could you add dark mode to the dashboard?" → Feature Request
- "App crashes when I upload files" → Bug/Technical Issue
- "How do I export my data?" → General Question
- "Click here to claim free crypto" → Spam / Abuse

Ticket: {ticket_text}

Respond with ONLY the category name from the approved list."""

        # 2. Try AI (Gemini/OpenAI) if rules failed
        
        ai_result = None
        
        # Try Gemini first
        if self.gemini_available:
            try:
                def classify_with_gemini():
                    response = self.gemini_model.generate_content(prompt)
                    category = response.text.strip()
                    return {
                        'category': category,
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
                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a ticket classification system. Respond with ONLY the category name."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=50,
                        temperature=0.3
                    )
                    category = response.choices[0].message.content.strip()
                    return {
                        'category': category,
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
        
        # If we get here, all providers failed
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
