"""
Comprehensive tests for providers/multi_provider.py
Tests CircuitBreaker and MultiProvider
"""
import pytest
from providers.multi_provider import (
    CircuitBreaker, 
    CircuitState, 
    MultiProvider
)
from unittest.mock import Mock, patch
import os


def test_circuit_breaker_initial_state():
    """Test circuit breaker initial state"""
    cb = CircuitBreaker()
    assert cb.state == CircuitState.CLOSED
    assert cb.failures == 0
    assert cb.last_failure_time is None

def test_circuit_breaker_success():
    """Test circuit breaker on successful call"""
    cb = CircuitBreaker()
    
    def success_func():
        return "success"
    
    result = cb.call(success_func)
    assert result == "success"
    assert cb.state == CircuitState.CLOSED
    assert cb.failures == 0

def test_circuit_breaker_failure():
    """Test circuit breaker on failure"""
    cb = CircuitBreaker(failure_threshold=3)
    
    def fail_func():
        raise Exception("Test error")
    
    # Fail 3 times
    for _ in range(3):
        try:
            cb.call(fail_func)
        except:
            pass
    
    assert cb.state == CircuitState.OPEN
    assert cb.failures == 3

def test_circuit_breaker_half_open():
    """Test circuit breaker half-open state"""
    cb = CircuitBreaker(failure_threshold=2, timeout=1)
    
    def fail_func():
        raise Exception("Test error")
    
    # Open circuit
    for _ in range(2):
        try:
            cb.call(fail_func)
        except:
            pass
    
    assert cb.state == CircuitState.OPEN
    
    # Wait and try again (should go to half-open)
    import time
    time.sleep(1.1)
    
    def success_func():
        return "success"
    
    result = cb.call(success_func)
    assert result == "success"
    assert cb.state == CircuitState.CLOSED

def test_circuit_breaker_open_blocks():
    """Test that open circuit blocks calls"""
    cb = CircuitBreaker(failure_threshold=2, timeout=60)
    
    def fail_func():
        raise Exception("Test error")
    
    # Open circuit
    for _ in range(2):
        try:
            cb.call(fail_func)
        except:
            pass
    
    assert cb.state == CircuitState.OPEN
    
    # Should raise exception
    with pytest.raises(Exception, match="Circuit breaker is open"):
        cb.call(fail_func)

def test_multi_provider_initialization_no_keys(mocker):
    """Test MultiProvider initialization without API keys"""
    mocker.patch.dict(os.environ, {}, clear=True)
    
    provider = MultiProvider()
    assert provider.gemini_available is False
    assert provider.openai_available is False

def test_multi_provider_get_status(mocker):
    """Test getting provider status"""
    provider = MultiProvider()
    status = provider.get_status()
    
    assert 'gemini' in status
    assert 'openai' in status
    assert status['gemini'] in ['available', 'unavailable']
    assert status['openai'] in ['available', 'unavailable']

def test_multi_provider_classify_no_providers(mocker):
    """Test classification when no providers available"""
    # Patch ALLOW_PROVIDERLESS to False so the test expects an exception
    with patch.dict(os.environ, {'ALLOW_PROVIDERLESS': 'false'}):
        # Create a new provider instance with the patched environment
        with patch('providers.multi_provider.os.getenv') as mock_getenv:
            def getenv_side_effect(key, default=''):
                if key == 'ALLOW_PROVIDERLESS':
                    return 'false'
                return os.environ.get(key, default)
            mock_getenv.side_effect = getenv_side_effect
            
            provider = MultiProvider()
            provider.gemini_available = False
            provider.openai_available = False
            provider.allow_providerless = False  # Explicitly set to False
            
            with pytest.raises(Exception, match="No AI providers available"):
                provider.classify("Test ticket")

def test_multi_provider_classify_with_gemini(mocker):
    """Test classification with Gemini provider"""
    provider = MultiProvider()
    provider.gemini_available = True
    provider.openai_available = False
    
    # Mock Gemini model
    mock_response = Mock()
    mock_response.text = "Network Issue"
    mock_model = Mock()
    mock_model.generate_content.return_value = mock_response
    provider.gemini_model = mock_model
    
    # Mock rule classifier to return None (force fallback to AI)
    provider.rule_classifier = Mock()
    provider.rule_classifier.classify.return_value = None
    
    result = provider.classify("Application dashboard throws error code 42")
    assert 'category' in result
    assert result['provider'] == 'gemini'

def test_multi_provider_rule_engine_short_circuit():
    """Rule engine should classify obvious tickets without hitting providers"""
    provider = MultiProvider()
    provider.gemini_available = True
    provider.openai_available = True

    result = provider.classify("I cannot connect to VPN and the network is down")
    assert result['provider'] == 'rule_engine'
    assert result['category'] == 'Network Issue'

def test_multi_provider_classify_fallback_to_openai(mocker):
    """Test classification fallback to OpenAI when Gemini fails"""
    from providers.multi_provider import MultiProvider, CircuitState
    
    provider = MultiProvider()
    # Set Gemini circuit to OPEN (failed) and OpenAI available
    provider.gemini_available = True
    provider.gemini_circuit.state = CircuitState.OPEN  # Gemini circuit is open (failed)
    provider.openai_available = True
    provider.openai_circuit.state = CircuitState.CLOSED  # OpenAI circuit is closed (available)
    
    # Mock Gemini to fail (circuit is open, so it won't be called, but ensure it's not available)
    # Actually, if circuit is OPEN, classify should skip Gemini and use OpenAI
    # But we need to ensure Gemini classify raises exception or returns None
    
    # Mock OpenAI client
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "Account Problem"
    mock_client.chat.completions.create.return_value = mock_response
    provider.openai_client = mock_client
    
    # When circuit is OPEN, circuit.call() will raise Exception("Circuit breaker is open")
    # So Gemini will fail and fallback to OpenAI
    # Mock the circuit.call to raise Exception for Gemini
    def mock_gemini_call(func):
        raise Exception("Circuit breaker is open")
    
    provider.gemini_circuit.call = mock_gemini_call
    
    # Mock rule classifier to return None (force fallback to AI)
    provider.rule_classifier = Mock()
    provider.rule_classifier.classify.return_value = None
    
    result = provider.classify("My account is locked")
    assert 'category' in result
    # Should use OpenAI since Gemini circuit is open and raises error
    assert result['provider'] == 'openai'

def test_multi_provider_circuit_breaker_integration(mocker):
    """Test circuit breaker integration in MultiProvider"""
    provider = MultiProvider()
    provider.gemini_available = True
    provider.openai_available = False
    
    # Mock Gemini to fail multiple times
    mock_model = Mock()
    mock_model.generate_content.side_effect = Exception("API Error")
    provider.gemini_model = mock_model
    
    # Mock rule classifier to return None (force fallback to AI)
    provider.rule_classifier = Mock()
    provider.rule_classifier.classify.return_value = None
    
    # Should fail and open circuit
    for _ in range(5):
        try:
            provider.classify("Test")
        except:
            pass
    
    # Circuit should be open
    assert provider.gemini_circuit.state == CircuitState.OPEN

def test_multi_provider_determine_priority():
    """Test priority determination"""
    provider = MultiProvider()
    
    priorities = {
        'Network Issue': 'high',
        'Account Problem': 'medium',
        'Billing Issue': 'critical',  # Payment Issue normalizes to Billing Issue which is critical
        'Feature Request': 'low',
        'Other': 'medium'
    }
    
    for category, expected_priority in priorities.items():
        priority = provider._determine_priority(category)
        assert priority == expected_priority
