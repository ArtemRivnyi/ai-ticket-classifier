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

from utils.rule_engine import (
    RuleEngine,
    VALID_CATEGORIES,
    SUBCATEGORIES,
    CATEGORY_SYNONYMS,
    PRIORITY_MAP,
    CRITICAL_KEYWORDS,
    BLACKLIST_KEYWORDS,
    CATEGORY_PRECEDENCE,
    SUBCATEGORY_PRIORITY_OVERRIDES
)

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
        self.rule_classifier = RuleEngine()
        
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
        # Use priority from result if already set (e.g., from rule_engine)
        if 'priority' in result and result['priority']:
            priority = result['priority']
        else:
            priority = PRIORITY_MAP.get(normalized, 'medium')
            
            # Check for subcategory overrides
            if (normalized, subcategory) in SUBCATEGORY_PRIORITY_OVERRIDES:
                priority = SUBCATEGORY_PRIORITY_OVERRIDES[(normalized, subcategory)]
        
        # Check for CRITICAL keywords (override unless already critical)
        if self._is_critical(ticket_text):
            priority = 'critical'
            
        # Check for LOW priority keywords (override unless already set to something else specific?)
        # Actually, low priority keywords should probably override medium/high if it's clearly a minor issue
        if self._is_low_priority(ticket_text) and priority != 'critical':
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
