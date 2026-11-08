"""Asynchronous Circuit Breaker pattern for external market data providers."""

import time
from typing import Literal

CircuitState = Literal["CLOSED", "OPEN", "HALF_OPEN"]


class CircuitBreakerOpenError(Exception):
    """Raised when an operation is attempted while the circuit breaker is OPEN."""
    pass


class CircuitBreaker:
    """Manages failure tracking and fail-fast behavior for external network calls."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout_sec: float = 30.0,
        half_open_success_threshold: int = 1,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        self.half_open_success_threshold = half_open_success_threshold

        self._state: CircuitState = "CLOSED"
        self._failure_count: int = 0
        self._success_count: int = 0
        self._last_state_change: float = time.monotonic()

    @property
    def state(self) -> CircuitState:
        if self._state == "OPEN":
            if time.monotonic() - self._last_state_change >= self.recovery_timeout_sec:
                self._state = "HALF_OPEN"
                self._success_count = 0
                self._last_state_change = time.monotonic()
        return self._state

    async def __aenter__(self):
        current_state = self.state
        if current_state == "OPEN":
            raise CircuitBreakerOpenError(
                f"Circuit breaker is OPEN (cooldown: {self.recovery_timeout_sec}s)"
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Operation failed
            self._failure_count += 1
            self._last_state_change = time.monotonic()
            if self._state in ("CLOSED", "HALF_OPEN") and self._failure_count >= self.failure_threshold:
                self._state = "OPEN"
            return False  # Let exception propagate

        # Operation succeeded
        if self.state == "HALF_OPEN":
            self._success_count += 1
            if self._success_count >= self.half_open_success_threshold:
                self._state = "CLOSED"
                self._failure_count = 0
                self._last_state_change = time.monotonic()
        elif self.state == "CLOSED":
            self._failure_count = 0

        return False
