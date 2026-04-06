import pytest
from unittest.mock import Mock
from utils.retry import retry, circuit_breaker
from utils.errors import APIError
import time


def test_retry_success():
    """Test retry decorator success case"""
    mock_func = Mock(return_value="success")
    decorated = retry(attempts=3, exceptions=(ValueError,))(mock_func)
    assert decorated() == "success"
    assert mock_func.call_count == 1


def test_retry_failure():
    """Test retry decorator failure case"""
    mock_func = Mock(side_effect=ValueError("fail"))
    decorated = retry(attempts=3, base_delay=0.01, exceptions=(ValueError,))(mock_func)
    with pytest.raises(ValueError):
        decorated()
    assert mock_func.call_count == 3


def test_circuit_breaker_success():
    """Test circuit breaker success"""
    mock_func = Mock(return_value="success")
    decorated = circuit_breaker(failure_threshold=2)(mock_func)
    assert decorated() == "success"


def test_circuit_breaker_open():
    """Test circuit breaker opens after failures"""
    mock_func = Mock(side_effect=ValueError("fail"))
    decorated = circuit_breaker(failure_threshold=2, recovery_timeout=1)(mock_func)

    # Fail twice
    with pytest.raises(ValueError):
        decorated()
    with pytest.raises(ValueError):
        decorated()

    # Should be open now
    with pytest.raises(RuntimeError, match="Circuit breaker is open"):
        decorated()
