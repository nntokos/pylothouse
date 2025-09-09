class PylothouseError(Exception):
    """Base exception for pylothouse suite."""


class ConfigError(PylothouseError):
    """Configuration-related errors."""


class PluginError(PylothouseError):
    """Plugin registration/lookup errors."""

