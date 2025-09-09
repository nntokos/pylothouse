from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, Optional

from .errors import PluginError

_REGISTRY: Dict[str, Any] = {}


def register_plugin(name: str, obj: Any) -> None:
    """Register a plugin object under a unique name."""
    if name in _REGISTRY:
        raise PluginError(f"Plugin '{name}' is already registered")
    _REGISTRY[name] = obj


def get_plugin(name: str) -> Any:
    """Retrieve a registered plugin by name."""
    try:
        return _REGISTRY[name]
    except KeyError as e:
        raise PluginError(f"Plugin '{name}' not found") from e


def list_plugins() -> Iterable[str]:
    """List registered plugin names."""
    return sorted(_REGISTRY.keys())


def load_entrypoint_plugins(group: str = "pylothouse.plugins") -> int:
    """Load plugins from entry points if available.

    Returns the number of loaded plugins. Entry points must expose a callable
    that returns a mapping of name->object or directly a plugin object, in which
    case the entry point name is used.
    """
    try:
        from importlib.metadata import entry_points  # Python 3.10+
    except Exception:  # pragma: no cover
        return 0

    count = 0
    try:
        eps = entry_points().select(group=group)  # type: ignore[attr-defined]
    except Exception:
        return 0

    for ep in eps:
        try:
            obj = ep.load()
            if callable(obj):
                produced = obj()
                if isinstance(produced, dict):
                    for name, item in produced.items():
                        register_plugin(name, item)
                        count += 1
                else:
                    register_plugin(ep.name, produced)
                    count += 1
            else:
                register_plugin(ep.name, obj)
                count += 1
        except Exception as exc:  # pragma: no cover
            # Swallow plugin load errors to avoid breaking core
            from .logging import get_logger

            get_logger(__name__).warning("Failed to load plugin '%s': %s", ep.name, exc)
    return count
# pylothouse-core

Core utilities for the pylothouse suite: configuration, errors, logging, and a simple plugin registry.

Install
```bash
pip install pylothouse-core
```

From monorepo (local dev)
```bash
pip install -e ./packages/pylothouse-core
```

