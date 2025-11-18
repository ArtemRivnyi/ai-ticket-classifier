"""Generic retry and circuit breaker helpers."""
from __future__ import annotations

import logging
import random
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Deque, Iterable, Tuple, Type

logger = logging.getLogger(__name__)


@dataclass
class CircuitBreakerState:
    """Internal state holder for the circuit breaker."""

    failure_threshold: int
    recovery_timeout: int
    consecutive_failures: int = 0
    last_failure_time: datetime | None = None
    is_open: bool = False

    def record_success(self) -> None:
        self.consecutive_failures = 0
        self.is_open = False
        self.last_failure_time = None

    def record_failure(self) -> None:
        self.consecutive_failures += 1
        self.last_failure_time = datetime.utcnow()
        if self.consecutive_failures >= self.failure_threshold:
            self.is_open = True

    def can_attempt(self) -> bool:
        if not self.is_open:
            return True
        if not self.last_failure_time:
            return True
        elapsed = datetime.utcnow() - self.last_failure_time
        return elapsed >= timedelta(seconds=self.recovery_timeout)


def retry(
    exceptions: Iterable[Type[BaseException]] | Tuple[Type[BaseException], ...],
    attempts: int = 3,
    base_delay: float = 0.2,
    max_delay: float = 2.0,
    jitter: float = 0.1,
) -> Callable:
    """Retry decorator with exponential backoff and jitter."""

    if not isinstance(exceptions, tuple):
        exceptions = tuple(exceptions)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:  # type: ignore[misc]
                    if attempt == attempts:
                        raise
                    sleep_for = min(delay, max_delay) + random.uniform(0, jitter)
                    logger.warning(
                        "Retrying function due to exception",
                        extra={
                            "attempt": attempt,
                            "max_attempts": attempts,
                            "sleep_for": round(sleep_for, 2),
                            "error": str(exc),
                        },
                    )
                    time.sleep(sleep_for)
                    delay *= 2

        return wrapper

    return decorator


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
) -> Callable:
    """Circuit breaker decorator to block failing dependencies."""

    def decorator(func: Callable) -> Callable:
        state = CircuitBreakerState(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
        )
        failure_window: Deque[datetime] = deque(maxlen=failure_threshold)

        @wraps(func)
        def wrapper(*args, **kwargs):
            if not state.can_attempt():
                raise RuntimeError("Circuit breaker is open")

            try:
                result = func(*args, **kwargs)
                state.record_success()
                failure_window.clear()
                return result
            except Exception as exc:  # noqa: BLE001
                failure_window.append(datetime.utcnow())
                state.record_failure()
                logger.warning(
                    "Circuit breaker failure",
                    extra={
                        "failures": state.consecutive_failures,
                        "threshold": state.failure_threshold,
                        "error": str(exc),
                    },
                )
                raise

        return wrapper

    return decorator
