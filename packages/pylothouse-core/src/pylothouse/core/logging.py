from __future__ import annotations

import logging
import os
from typing import Optional

_DEFAULT_FMT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def setup_logging(level: Optional[str] = None, fmt: Optional[str] = None) -> None:
    """Configure root logging once.

    Args:
        level: Log level name; falls back to env PYLH_LOG_LEVEL or INFO.
        fmt: Log format string; falls back to default.
    """
    if getattr(setup_logging, "_configured", False):
        return
    lvl = (level or os.getenv("PYLH_LOG_LEVEL") or "INFO").upper()
    try:
        numeric_level = getattr(logging, lvl)
    except AttributeError:
        numeric_level = logging.INFO
    logging.basicConfig(level=numeric_level, format=fmt or _DEFAULT_FMT)
    setup_logging._configured = True  # type: ignore[attr-defined]


def get_logger(name: str) -> logging.Logger:
    """Get a namespaced logger; ensures logging is configured."""
    setup_logging()
    return logging.getLogger(name)

