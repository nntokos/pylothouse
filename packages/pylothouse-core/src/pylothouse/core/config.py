from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .errors import ConfigError


@dataclass
class Config:
    """Minimal config object for pylothouse.

    Reads from environment variables with prefix PYLH_. Add fields as needed.
    """
    log_level: str = "INFO"

    @classmethod
    def from_env(cls, env: Optional[Dict[str, str]] = None) -> "Config":
        e = env or os.environ
        return cls(
            log_level=e.get("PYLH_LOG_LEVEL", cls.log_level),
        )


_cached: Optional[Config] = None


def get_config(overrides: Optional[Dict[str, Any]] = None) -> Config:
    """Get process-wide config with optional overrides.

    Args:
        overrides: mapping of field->value to override env-derived defaults.
    Raises:
        ConfigError: if overrides contain unknown keys.
    """
    global _cached
    if _cached is None:
        _cached = Config.from_env()
    if overrides:
        unknown = set(overrides) - set(_cached.__dict__)
        if unknown:
            raise ConfigError(f"Unknown config keys: {sorted(unknown)}")
        for k, v in overrides.items():
            setattr(_cached, k, v)
    return _cached

