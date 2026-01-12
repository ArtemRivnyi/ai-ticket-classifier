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
    CATEGORY_PRECEDENCE,
    SUBCATEGORY_PRIORITY_OVERRIDES,
)
from utils.prompt_formatter import format_classification_prompt
from tenacity import retry, stop_after_attempt, wait_exponential


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
        self.allow_providerless = (
            os.getenv("ALLOW_PROVIDERLESS", "false").lower() == "true"
        )
        self.gemini_circuit = CircuitBreaker()
        self.openai_circuit = CircuitBreaker()
        self.rule_classifier = RuleEngine()

        # Initialize Gemini using GeminiClassifier
        try:
            from providers.gemini_provider import GeminiClassifier

            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.warning("⚠️ GEMINI_API_KEY not found")
            else:
                try:
                    self.gemini_classifier = GeminiClassifier()
                    self.gemini_available = True
                    logger.info("✅ Gemini provider initialized via GeminiClassifier")
                except Exception as e:
                    logger.warning(f"⚠️ Gemini provider failed: {e}")
        except ImportError as import_error:
            logger.warning(f"⚠️ GeminiClassifier not available: {import_error}")
        except Exception as e:
            logger.warning(f"⚠️ Gemini provider failed: {e}")

        # Initialize OpenAI (optional fallback)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            self.openai_available = True
            logger.info("✅ OpenAI provider initialized")
        else:
            logger.warning("⚠️ OPENAI_API_KEY not found")

    def classify(self, ticket_text: str) -> Dict:
        """
        Classify ticket using available providers with failover:
        1. Gemini (Primary)
        2. OpenAI (Secondary)
        3. Rule Engine (Fallback)
        """
        # 1. Try Gemini
        if self.gemini_available:
            try:
                return self.gemini_circuit.call(self.classify_with_gemini, ticket_text)
            except Exception as e:
                logger.warning(f"Gemini failed: {e}")

        # 2. Try OpenAI
        if self.openai_available:
            try:
                return self.openai_circuit.call(self.classify_with_openai, ticket_text)
            except Exception as e:
                logger.warning(f"OpenAI failed: {e}")

        # 3. Try Rule Engine as FALLBACK
        logger.info("⚠️ AI providers failed or unavailable, falling back to Rule Engine")
        rule_match = self.rule_classifier.classify(ticket_text)
        if rule_match:
            logger.info(f"✅ Rule Engine matched (fallback): {rule_match['category']}")
            return self._post_process_result(rule_match, ticket_text)

        # If we get here, all providers failed
        if self.allow_providerless:
            logger.info("Rule-only mode: returning fallback classification")
            fallback_result = {
                "category": "Other",
                "subcategory": "Unclassified",
                "confidence": 0.5,
                "provider": "fallback_rule_engine",
            }
            return self._post_process_result(fallback_result, ticket_text)
        raise Exception("All providers failed")

    def classify_with_gemini(self, ticket_text: str) -> Dict:
        """Classify using Gemini provider"""
        return self.gemini_classifier.classify(ticket_text)

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def classify_with_openai(self, ticket_text: str) -> Dict:
        """Classify using OpenAI provider"""
        # Placeholder for actual OpenAI implementation
        # For now, we'll simulate a failure if called, or implement basic if needed
        # But since we don't have the client initialized, we can't really call it.
        # Assuming the user wants the structure.
        # If we had the client, we would use it here.
        # For now, let's raise if not implemented or mock it if strictly required.
        # Given the context, I'll implement a basic request if key exists, or fail.

        if not self.openai_api_key:
            raise Exception("OpenAI API key not configured")

        try:
            import openai

            client = openai.OpenAI(api_key=self.openai_api_key)
            prompt = format_classification_prompt(ticket_text, provider="openai")

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a support ticket classifier. Return ONLY valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=150,
            )

            content = response.choices[0].message.content

            # Parse JSON response
            import json

            # Handle potential markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)

            # Ensure required fields
            result.setdefault("provider", "openai")
            if "confidence" not in result:
                result["confidence"] = 0.8

            return result

        except ImportError:
            logger.error("OpenAI library not installed")
            raise
        except Exception as e:
            logger.error(f"OpenAI classification failed: {e}")
            raise

    def _post_process_result(self, result: Dict, ticket_text: str) -> Dict:
        """Normalize category names and apply blacklist corrections"""
        category = result.get("category", "Other")
        normalized = self._normalize_category(category)

        if self._matches_blacklist(ticket_text):
            normalized = "Spam / Abuse"

        if normalized not in VALID_CATEGORIES:
            normalized = "Other"

        result["category"] = normalized

        # Validate subcategory
        subcategory = result.get("subcategory")
        if normalized in SUBCATEGORIES:
            valid_subs = SUBCATEGORIES[normalized]
            if subcategory not in valid_subs:
                # Try to find a matching subcategory or default to first/None
                result["subcategory"] = None
        else:
            result["subcategory"] = None

        # Determine priority
        # Use priority from result if already set (e.g., from rule_engine)
        if "priority" in result and result["priority"]:
            priority = result["priority"]
        else:
            priority = PRIORITY_MAP.get(normalized, "medium")

            # Check for subcategory overrides
            if (normalized, subcategory) in SUBCATEGORY_PRIORITY_OVERRIDES:
                priority = SUBCATEGORY_PRIORITY_OVERRIDES[(normalized, subcategory)]

        # Check for CRITICAL keywords (override unless already critical)
        if self._is_critical(ticket_text):
            priority = "critical"

        # Check for LOW priority keywords (override unless already set to something else specific?)
        # Actually, low priority keywords should probably override medium/high if it's clearly a minor issue
        if self._is_low_priority(ticket_text) and priority != "critical":
            priority = "low"

        result["priority"] = priority

        if "confidence" not in result or result["confidence"] is None:
            result["confidence"] = 0.75
        return result

    def _normalize_category(self, category: Optional[str]) -> str:
        if not category:
            return "Other"
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
            r"cosmetic",
            r"typo",
            r"color",
            r"alignment",
            r"spacing",
            r"minor",
            r"not\s+urgent",
            r"nice\s+to\s+have",
            r"suggestion",
        ]
        return any(re.search(pattern, text) for pattern in low_keywords)

    def _determine_priority(self, category: Optional[str]) -> str:
        """Backward-compatible priority helper used in tests."""
        normalized = self._normalize_category(category or "Other")
        return PRIORITY_MAP.get(normalized, "medium")

    def _matches_blacklist(self, ticket_text: str) -> bool:
        text = ticket_text.lower()
        return any(re.search(pattern, text) for pattern in BLACKLIST_KEYWORDS)

    def get_status(self) -> Dict:
        """Get provider availability status"""
        return {
            "gemini": "available" if self.gemini_available else "unavailable",
            "openai": "available" if self.openai_available else "unavailable",
        }


# Alias for backward compatibility
class MultiProviderClassifier(MultiProvider):
    """
    Wrapper class for backward compatibility
    The app.py expects MultiProviderClassifier, so we provide it as an alias
    """

    pass
