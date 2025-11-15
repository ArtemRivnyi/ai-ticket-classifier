"""
Multi-Provider System for AI Classification
Supports Gemini as primary and OpenAI as fallback
"""

import os
import logging
import time
from typing import Dict, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


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
        
        # Initialize Gemini
        try:
            import google.generativeai as genai
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                self.gemini_available = True
                logger.info("✅ Gemini provider initialized")
            else:
                logger.warning("⚠️ GEMINI_API_KEY not found")
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
        
        if not self.gemini_available and not self.openai_available:
            raise Exception("No AI providers available. Please set GEMINI_API_KEY or OPENAI_API_KEY")
        
        logger.info(f"🚀 MultiProvider initialized (Gemini: {self.gemini_available}, OpenAI: {self.openai_available})")
    
    def classify(self, ticket_text: str) -> Dict:
        """Classify ticket using available provider"""
        
        prompt = f"""Classify this support ticket into ONE of these categories:
- Network Issue
- Account Problem  
- Payment Issue
- Feature Request
- Other

Ticket: {ticket_text}

Respond with ONLY the category name, nothing else."""

        # Try Gemini first
        if self.gemini_available:
            try:
                def classify_with_gemini():
                    response = self.gemini_model.generate_content(prompt)
                    category = response.text.strip()
                    return {
                        'category': category,
                        'confidence': 0.95,
                        'priority': self._determine_priority(category),
                        'provider': 'gemini'
                    }
                
                return self.gemini_circuit.call(classify_with_gemini)
                
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
                            {"role": "system", "content": "You are a ticket classification system."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=50,
                        temperature=0.3
                    )
                    category = response.choices[0].message.content.strip()
                    return {
                        'category': category,
                        'confidence': 0.90,
                        'priority': self._determine_priority(category),
                        'provider': 'openai'
                    }
                
                return self.openai_circuit.call(classify_with_openai)
                
            except Exception as e:
                logger.error(f"OpenAI classification failed: {e}")
                raise
        
        raise Exception("All providers failed")
    
    def _determine_priority(self, category: str) -> str:
        """Determine priority based on category"""
        priority_map = {
            'Network Issue': 'high',
            'Account Problem': 'high',
            'Payment Issue': 'high',
            'Feature Request': 'low',
            'Other': 'medium'
        }
        return priority_map.get(category, 'medium')
    
    def get_status(self) -> Dict:
        """Get provider availability status"""
        return {
            'gemini': 'available' if self.gemini_available else 'unavailable',
            'openai': 'available' if self.openai_available else 'unavailable'
        }


# Alias для обратной совместимости
class MultiProviderClassifier(MultiProvider):
    """
    Wrapper class for backward compatibility
    The app.py expects MultiProviderClassifier, so we provide it as an alias
    """
    pass
