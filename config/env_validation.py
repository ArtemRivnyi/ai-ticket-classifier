"""
Environment validation utilities to enforce required configuration
for production deployments. Missing critical variables should fail
startup (except during unit tests).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List


@dataclass
class EnvironmentStatus:
    """Represents the outcome of environment validation."""

    missing: List[str]
    warnings: List[str]

    @property
    def is_valid(self) -> bool:
        return len(self.missing) == 0


REQUIRED_VARS = [
    "MASTER_API_KEY",
    "SECRET_KEY",
]

# At least one provider key must be configured
PROVIDER_VARS = ["GEMINI_API_KEY", "OPENAI_API_KEY"]

OPTIONAL_WARNINGS = {
    "REDIS_URL": "Redis URL not set. Falling back to in-memory rate limiting.",
    "DATABASE_URL": "DATABASE_URL missing. Persistence features will be disabled.",
}


def validate_environment(skip_failure: bool = False) -> EnvironmentStatus:
    """
    Validate that all required environment variables are present.

    Args:
        skip_failure: When True, missing vars are reported but not considered fatal.

    Returns:
        EnvironmentStatus containing missing vars and warnings.
    """

    missing: List[str] = []
    warnings: List[str] = []

    for var in REQUIRED_VARS:
        if not os.getenv(var):
            missing.append(var)

    if not any(os.getenv(var) for var in PROVIDER_VARS):
        missing.append("GEMINI_API_KEY or OPENAI_API_KEY")

    for var, warning in OPTIONAL_WARNINGS.items():
        if not os.getenv(var):
            warnings.append(warning)

    if skip_failure:
        # When skipping failure (e.g., during tests) we downgrade missing vars to warnings
        warnings.extend(f"Missing required var (test mode): {var}" for var in missing)
        missing = []

    return EnvironmentStatus(missing=missing, warnings=warnings)

