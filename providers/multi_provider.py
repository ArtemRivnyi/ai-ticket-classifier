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
    'Network Issue',
    'Account Problem',
    'Payment Issue',
    'Feature Request',
    'Spam / Abuse',
    'Other'
]

CATEGORY_SYNONYMS = {
    'network': 'Network Issue',
    'vpn issue': 'Network Issue',
    'connectivity': 'Network Issue',
    'account': 'Account Problem',
    'login': 'Account Problem',
    'password': 'Account Problem',
    'billing': 'Payment Issue',
    'refund': 'Payment Issue',
    'charge': 'Payment Issue',
    'idea': 'Feature Request',
    'suggestion': 'Feature Request',
    'spam': 'Spam / Abuse',
    'abuse': 'Spam / Abuse',
    'phishing': 'Spam / Abuse'
}

PRIORITY_MAP = {
    'Network Issue': 'high',
    'Account Problem': 'high',
    'Payment Issue': 'high',
    'Spam / Abuse': 'medium',
    'Feature Request': 'low',
    'Other': 'medium'
}

BLACKLIST_KEYWORDS = [
    r'free money',
    r'visit .*bitcoin',
    r'click here',
    r'phishing',
    r'buy now'
]


class RuleBasedClassifier:
    """Deterministic regex/keyword rules for obvious cases."""

    def __init__(self):
        self.rules: List[Dict] = [
            {
                'category': 'Network Issue',
                'patterns': [r'\bvpn\b', r'\bnetwork\b', r'\binternet\b', r'\bwifi\b', r'latency']
            },
            {
                'category': 'Account Problem',
                'patterns': [r'password', r'login', r'sign[\s-]?in', r'locked account']
            },
            {
                'category': 'Payment Issue',
                'patterns': [r'invoice', r'charge', r'billing', r'payment', r'refund']
            },
            {
                'category': 'Feature Request',
                'patterns': [r'would like', r'feature request', r'could you add', r'enhancement']
            },
            {
                'category': 'Spam / Abuse',
                'patterns': [r'unsubscribe', r'spam', r'phishing', r'crypto', r'promo']
            },
        ]

    def classify(self, ticket_text: str) -> Optional[Dict]:
        text = ticket_text.lower()
        for rule in self.rules:
            if any(re.search(pattern, text) for pattern in rule['patterns']):
                category = rule['category']
                return {
                    'category': category,
                    'confidence': 1.0,
                    'priority': PRIORITY_MAP.get(category, 'medium'),
                    'provider': 'rule_engine'
                }
        return None


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
        """Classify ticket using available provider"""
        
        # Check if any provider is available
        if not self.gemini_available and not self.openai_available:
            raise Exception("No AI providers available. Please set GEMINI_API_KEY or OPENAI_API_KEY")
        
        prompt = f"""
You are an AI assistant that classifies support tickets into EXACTLY one of the approved categories.

Allowed categories (respond with one of them verbatim):
1. Network Issue — connectivity, VPN, latency, networking
2. Account Problem — login, password, user profile
3. Payment Issue — billing, charges, refunds, invoices
4. Feature Request — enhancements, suggestions, roadmap asks
5. Spam / Abuse — phishing, unsolicited promos, abuse
6. Other — anything that does not match above

Examples:
- "VPN is down for the whole office" -> Network Issue
- "Please refund the duplicate charge from yesterday" -> Payment Issue
- "I need to reset my password again" -> Account Problem
- "Could you add dark mode to the dashboard?" -> Feature Request
- "Click here to claim free crypto" -> Spam / Abuse

Ticket: {ticket_text}

Respond with ONLY the category name from the approved list."""

        # Deterministic rules first
        rule_match = self.rule_classifier.classify(ticket_text)
        if rule_match:
            return self._post_process_result(rule_match, ticket_text)

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
                
                result = self.gemini_circuit.call(classify_with_gemini)
                return self._post_process_result(result, ticket_text)
                
            except Exception as e:
                logger.error(f"Gemini classification failed: {e}")
                if not self.openai_available:
                    raise
        
        # Fallback to OpenAI if Gemini fails
        if self.openai_available:
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
                
                result = self.openai_circuit.call(classify_with_openai)
                return self._post_process_result(result, ticket_text)
                
            except Exception as e:
                logger.error(f"OpenAI classification failed: {e}")
                # If both providers failed, raise error
                if not self.gemini_available:
                    raise
        
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
        result['priority'] = PRIORITY_MAP.get(normalized, 'medium')
        if 'confidence' not in result or result['confidence'] is None:
            result['confidence'] = 0.75
        return result

    def _determine_priority(self, category: Optional[str]) -> str:
        """Backward-compatible priority helper used in tests."""
        normalized = self._normalize_category(category or 'Other')
        return PRIORITY_MAP.get(normalized, 'medium')

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
