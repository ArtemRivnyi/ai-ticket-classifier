# providers/multi_provider.py
"""
Multi-Provider Fallback System с Circuit Breaker
Поддержка: Gemini, OpenAI, Anthropic (Claude)
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field
import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Состояния Circuit Breaker"""
    CLOSED = "closed"      # Нормальная работа
    OPEN = "open"          # Провайдер недоступен
    HALF_OPEN = "half_open"  # Проверка восстановления


@dataclass
class CircuitBreaker:
    """Circuit Breaker для защиты от падений провайдера"""
    failure_threshold: int = 5  # Количество ошибок до открытия
    timeout_seconds: int = 60   # Время до повторной попытки
    half_open_attempts: int = 3  # Попыток в HALF_OPEN состоянии
    
    state: CircuitState = CircuitState.CLOSED
    failures: int = 0
    last_failure_time: Optional[datetime] = None
    success_count: int = 0
    
    def record_success(self):
        """Записать успешный вызов"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_attempts:
                logger.info("🟢 Circuit breaker CLOSED - provider recovered")
                self.state = CircuitState.CLOSED
                self.failures = 0
                self.success_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failures = max(0, self.failures - 1)  # Постепенное восстановление
    
    def record_failure(self):
        """Записать неудачный вызов"""
        self.failures += 1
        self.last_failure_time = datetime.now()
        self.success_count = 0
        
        if self.failures >= self.failure_threshold:
            if self.state != CircuitState.OPEN:
                logger.warning(f"🔴 Circuit breaker OPEN - {self.failures} failures")
            self.state = CircuitState.OPEN
    
    def can_attempt(self) -> bool:
        """Можно ли попробовать вызов?"""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.HALF_OPEN:
            return True
        
        # State is OPEN - check timeout
        if self.last_failure_time:
            time_passed = datetime.now() - self.last_failure_time
            if time_passed > timedelta(seconds=self.timeout_seconds):
                logger.info("🟡 Circuit breaker HALF_OPEN - testing provider")
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                return True
        
        return False
    
    def get_state_info(self) -> Dict:
        """Получить информацию о состоянии"""
        return {
            'state': self.state.value,
            'failures': self.failures,
            'threshold': self.failure_threshold,
            'last_failure': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'can_attempt': self.can_attempt()
        }


@dataclass
class ProviderConfig:
    """Конфигурация провайдера"""
    name: str
    api_key: str
    priority: int  # 1 = primary, 2 = secondary, etc.
    enabled: bool = True
    circuit_breaker: CircuitBreaker = field(default_factory=CircuitBreaker)
    max_retries: int = 2
    timeout_seconds: int = 30


class AIProvider:
    """Базовый класс для AI провайдеров"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.name = config.name
    
    def classify(self, ticket_text: str) -> Dict:
        """Классифицировать тикет - должен быть переопределен"""
        raise NotImplementedError
    
    def is_available(self) -> bool:
        """Проверить доступность провайдера"""
        return (
            self.config.enabled and
            self.config.api_key and
            self.config.circuit_breaker.can_attempt()
        )


class GeminiProvider(AIProvider):
    """Google Gemini провайдер"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        genai.configure(api_key=config.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        logger.info(f"✓ Gemini provider initialized")
    
    def classify(self, ticket_text: str) -> Dict:
        """Классификация через Gemini"""
        prompt = f"""Classify this support ticket into one of these categories:
- IT Support
- Billing
- Account Access
- Feature Request
- Bug Report
- Other

Ticket: {ticket_text}

Respond in JSON format:
{{"category": "category_name", "confidence": 0.95, "reasoning": "brief explanation"}}"""
        
        response = self.model.generate_content(prompt)
        
        # Парсинг ответа
        import json
        import re
        
        text = response.text
        # Извлечь JSON из возможного markdown блока
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            result['provider'] = 'gemini'
            return result
        
        raise ValueError(f"Invalid Gemini response: {text}")


class OpenAIProvider(AIProvider):
    """OpenAI провайдер"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = OpenAI(api_key=config.api_key)
        logger.info(f"✓ OpenAI provider initialized")
    
    def classify(self, ticket_text: str) -> Dict:
        """Классификация через OpenAI"""
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # Быстрая и дешевая модель
            messages=[
                {"role": "system", "content": """You are a support ticket classifier.
Classify tickets into: IT Support, Billing, Account Access, Feature Request, Bug Report, Other.
Respond ONLY with JSON: {"category": "name", "confidence": 0.95, "reasoning": "why"}"""},
                {"role": "user", "content": ticket_text}
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        result['provider'] = 'openai'
        return result


class AnthropicProvider(AIProvider):
    """Anthropic Claude провайдер"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = Anthropic(api_key=config.api_key)
        logger.info(f"✓ Anthropic provider initialized")
    
    def classify(self, ticket_text: str) -> Dict:
        """Классификация через Claude"""
        message = self.client.messages.create(
            model="claude-3-haiku-20240307",  # Быстрая модель
            max_tokens=150,
            messages=[{
                "role": "user",
                "content": f"""Classify this support ticket into one category:
IT Support, Billing, Account Access, Feature Request, Bug Report, Other

Ticket: {ticket_text}

Respond ONLY with JSON: {{"category": "name", "confidence": 0.95, "reasoning": "why"}}"""
            }]
        )
        
        import json
        result = json.loads(message.content[0].text)
        result['provider'] = 'anthropic'
        return result


class MultiProviderClassifier:
    """
    Главный класс с автоматическим fallback между провайдерами
    """
    
    def __init__(self):
        self.providers: List[AIProvider] = []
        self._initialize_providers()
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'provider_usage': {}
        }
    
    def _initialize_providers(self):
        """Инициализация всех доступных провайдеров"""
        
        # 1. Primary: Gemini
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            config = ProviderConfig(
                name='gemini',
                api_key=gemini_key,
                priority=1,
                circuit_breaker=CircuitBreaker(
                    failure_threshold=5,
                    timeout_seconds=60
                )
            )
            self.providers.append(GeminiProvider(config))
            logger.info("✓ Gemini configured as PRIMARY provider")
        
        # 2. Fallback: OpenAI
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            config = ProviderConfig(
                name='openai',
                api_key=openai_key,
                priority=2,
                circuit_breaker=CircuitBreaker(
                    failure_threshold=3,
                    timeout_seconds=30
                )
            )
            self.providers.append(OpenAIProvider(config))
            logger.info("✓ OpenAI configured as FALLBACK provider")
        
        # 3. Fallback: Anthropic
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key:
            config = ProviderConfig(
                name='anthropic',
                api_key=anthropic_key,
                priority=3,
                circuit_breaker=CircuitBreaker(
                    failure_threshold=3,
                    timeout_seconds=30
                )
            )
            self.providers.append(AnthropicProvider(config))
            logger.info("✓ Anthropic configured as FALLBACK provider")
        
        # Сортировка по приоритету
        self.providers.sort(key=lambda p: p.config.priority)
        
        if not self.providers:
            raise ValueError("No AI providers configured! Set GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY")
        
        logger.info(f"🚀 MultiProvider initialized with {len(self.providers)} provider(s)")
    
    def classify(self, ticket_text: str, max_attempts: int = None) -> Dict:
        """
        Классифицировать тикет с автоматическим fallback
        
        Args:
            ticket_text: Текст тикета
            max_attempts: Максимум попыток (по умолчанию все провайдеры)
        
        Returns:
            Dict с результатом классификации
        
        Raises:
            Exception: Если все провайдеры недоступны
        """
        self.stats['total_requests'] += 1
        
        if max_attempts is None:
            max_attempts = len(self.providers)
        
        last_error = None
        attempts = 0
        
        for provider in self.providers:
            if attempts >= max_attempts:
                break
            
            if not provider.is_available():
                logger.warning(f"⏭️ Skipping {provider.name} - not available")
                continue
            
            attempts += 1
            
            try:
                logger.info(f"🔄 Attempting classification with {provider.name}")
                
                start_time = time.time()
                result = provider.classify(ticket_text)
                duration = time.time() - start_time
                
                # Успех!
                provider.config.circuit_breaker.record_success()
                self.stats['successful_requests'] += 1
                self.stats['provider_usage'][provider.name] = \
                    self.stats['provider_usage'].get(provider.name, 0) + 1
                
                result.update({
                    'provider': provider.name,
                    'processing_time_ms': round(duration * 1000, 2),
                    'attempt': attempts,
                    'total_providers': len(self.providers)
                })
                
                logger.info(f"✅ Success with {provider.name} in {duration:.2f}s")
                return result
                
            except Exception as e:
                last_error = e
                provider.config.circuit_breaker.record_failure()
                
                logger.error(f"❌ {provider.name} failed: {str(e)}")
                
                # Если это не последняя попытка, продолжаем
                if attempts < max_attempts:
                    logger.info(f"↪️ Falling back to next provider...")
                    time.sleep(0.5)  # Небольшая задержка перед fallback
                    continue
        
        # Все провайдеры упали
        self.stats['failed_requests'] += 1
        
        raise Exception(
            f"All {attempts} provider(s) failed. "
            f"Last error: {str(last_error)}. "
            f"Available providers: {[p.name for p in self.providers if p.is_available()]}"
        )
    
    def get_health_status(self) -> Dict:
        """Получить статус всех провайдеров"""
        return {
            'providers': [
                {
                    'name': p.name,
                    'priority': p.config.priority,
                    'enabled': p.config.enabled,
                    'available': p.is_available(),
                    'circuit_breaker': p.config.circuit_breaker.get_state_info()
                }
                for p in self.providers
            ],
            'stats': self.stats
        }
    
    def get_stats(self) -> Dict:
        """Получить статистику использования"""
        success_rate = 0
        if self.stats['total_requests'] > 0:
            success_rate = (self.stats['successful_requests'] / 
                          self.stats['total_requests']) * 100
        
        return {
            **self.stats,
            'success_rate': round(success_rate, 2),
            'providers_count': len(self.providers),
            'available_providers': sum(1 for p in self.providers if p.is_available())
        }


# ===== ИНТЕГРАЦИЯ С FLASK =====

from flask import Flask, request, jsonify

app = Flask(__name__)

# Инициализация multi-provider системы
try:
    classifier = MultiProviderClassifier()
except Exception as e:
    logger.error(f"Failed to initialize MultiProviderClassifier: {e}")
    classifier = None


@app.route('/api/v1/classify', methods=['POST'])
def classify_endpoint():
    """Endpoint для классификации с auto-fallback"""
    
    if not classifier:
        return jsonify({
            'error': 'Classification service unavailable',
            'message': 'No AI providers configured'
        }), 503
    
    data = request.json
    ticket_text = data.get('ticket')
    
    if not ticket_text:
        return jsonify({'error': 'Missing ticket text'}), 400
    
    try:
        result = classifier.classify(ticket_text)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        return jsonify({
            'error': 'Classification failed',
            'message': str(e),
            'providers_status': classifier.get_health_status()
        }), 500


@app.route('/api/v1/providers/health', methods=['GET'])
def providers_health():
    """Проверка здоровья всех провайдеров"""
    if not classifier:
        return jsonify({'error': 'Service unavailable'}), 503
    
    return jsonify(classifier.get_health_status())


@app.route('/api/v1/providers/stats', methods=['GET'])
def providers_stats():
    """Статистика использования провайдеров"""
    if not classifier:
        return jsonify({'error': 'Service unavailable'}), 503
    
    return jsonify(classifier.get_stats())


# ===== ТЕСТИРОВАНИЕ =====

if __name__ == '__main__':
    print("=" * 60)
    print("🧪 MULTI-PROVIDER FALLBACK TEST")
    print("=" * 60)
    
    # Создать тестовый classifier
    test_classifier = MultiProviderClassifier()
    
    # Тест 1: Нормальная классификация
    print("\n1️⃣ Testing normal classification...")
    try:
        result = test_classifier.classify("My laptop is broken")
        print(f"✅ Result: {result['category']} ({result['provider']}) - {result['confidence']}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Тест 2: Статус провайдеров
    print("\n2️⃣ Checking providers health...")
    health = test_classifier.get_health_status()
    for p in health['providers']:
        status = "🟢" if p['available'] else "🔴"
        print(f"{status} {p['name']}: {p['circuit_breaker']['state']}")
    
    # Тест 3: Симуляция падения primary провайдера
    print("\n3️⃣ Simulating primary provider failure...")
    if len(test_classifier.providers) > 1:
        # Принудительно открыть circuit breaker у первого провайдера
        test_classifier.providers[0].config.circuit_breaker.state = CircuitState.OPEN
        test_classifier.providers[0].config.circuit_breaker.failures = 10
        
        try:
            result = test_classifier.classify("Billing question")
            print(f"✅ Fallback worked! Used: {result['provider']}")
        except Exception as e:
            print(f"❌ Fallback failed: {e}")
    
    # Тест 4: Финальная статистика
    print("\n4️⃣ Final statistics:")
    stats = test_classifier.get_stats()
    print(f"Total requests: {stats['total_requests']}")
    print(f"Success rate: {stats['success_rate']}%")
    print(f"Provider usage: {stats['provider_usage']}")
    
    print("\n" + "=" * 60)
    print("✅ TESTS COMPLETED")
    print("=" * 60)