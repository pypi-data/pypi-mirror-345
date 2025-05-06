"""
Configuration module for DTA Observability.
"""

import logging
import os
from enum import Enum, auto
from typing import Any, Dict, Optional, Set

DEFAULT_CONFIG = {
    "SERVICE_NAME": "unnamed-service",
    "SERVICE_VERSION": "0.0.0",
    "SERVICE_INSTANCE_ID": "",
    "TRACES_EXPORTER": "otlp",
    "METRICS_EXPORTER": "otlp",
    "LOGS_EXPORTER": "otlp",
    "EXPORTER_OTLP_ENDPOINT": "http://localhost:4317",
    "EXPORTER_OTLP_INSECURE": "true",
    "OTEL_PROPAGATORS": "w3c,gcp,tracecontext",
    "BATCH_EXPORT_SCHEDULE_DELAY": "120000",
    "AUTO_INSTRUMENTATION_ENABLED": "true",
    "LOGGING_INSTRUMENTATION_ENABLED": "true",
    "SYSTEM_METRICS_ENABLED": "true",
    "RESOURCE_DETECTORS_ENABLED": "true",
    "LOG_LEVEL": "INFO",
    "SAFE_LOGGING": "true",
    "EXCLUDED_INSTRUMENTATIONS": "",
    "LOG_FORMAT": "default",
    "EXPORTER_TYPE": "",
}


class LogFormatType(str, Enum):
    """Log format types supported by the system."""

    DEFAULT = "default"
    GCP = "gcp"


class ConfigValueType(Enum):
    """Types of configuration values."""

    STRING = auto()
    BOOLEAN = auto()
    INTEGER = auto()


class ConfigurationManager:
    """
    Manages configuration for the DTA Observability SDK.
    Reads from environment variables with fallbacks to defaults.
    """

    _BOOLEAN_TRUE_VALUES: Set[str] = {"true", "1", "t", "yes", "y"}

    _ENV_PREFIXES: list[str] = ["OTEL_", "DTA_"]

    def __init__(self) -> None:
        self._config = self._load_from_env()

    def _load_from_env(self) -> Dict[str, str]:
        """Load configuration from environment variables with defaults."""
        config = DEFAULT_CONFIG.copy()

        for key in DEFAULT_CONFIG:
            env_value = os.environ.get(key)
            if env_value is not None:
                config[key] = env_value
                continue

            for prefix in self._ENV_PREFIXES:
                env_key = f"{prefix}{key}"
                env_value = os.environ.get(env_key)
                if env_value is not None:
                    config[key] = env_value
                    break

        return config

    def get(self, key: str) -> Optional[str]:
        """Get a configuration value by key."""
        return self._config.get(key)

    def get_boolean(self, key: str) -> bool:
        """Get a boolean configuration value by key."""
        value = self._config.get(key)
        if value is None:
            return False
        return value.lower() in self._BOOLEAN_TRUE_VALUES

    def get_int(self, key: str, default: int = 0) -> int:
        """Get an integer configuration value by key."""
        value = self._config.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:

            import logging

            logger = logging.getLogger("dta_observability.config")
            logger.warning(
                f"Config value for '{key}' could not be converted to integer: '{value}', using default: {default}"
            )
            return default

    def get_all(self) -> Dict[str, str]:
        """Get all configuration values."""
        return self._config.copy()

    def get_typed(self, key: str, value_type: ConfigValueType, default: Any = None) -> Any:
        """
        Get a strongly-typed configuration value by key and type.

        Args:
            key: The configuration key
            value_type: The type of value to retrieve
            default: Default value to return if key not found

        Returns:
            The configuration value converted to the requested type
        """
        if value_type == ConfigValueType.STRING:
            return self.get(key) or default
        elif value_type == ConfigValueType.BOOLEAN:
            if key not in self._config:
                return bool(default) if default is not None else False
            return self.get_boolean(key)
        elif value_type == ConfigValueType.INTEGER:
            return self.get_int(key, default or 0)
        return default


_config_manager = ConfigurationManager()


def get_config(key: Optional[str] = None) -> Any:
    """
    Get configuration value(s).

    Args:
        key: The configuration key to fetch. If None, returns all config.

    Returns:
        The configuration value or all configuration values if key is None.
    """
    if key is None:
        return _config_manager.get_all()
    return _config_manager.get(key)


def get_boolean_config(key: str, default: bool = False) -> bool:
    """
    Get a boolean configuration value.

    Args:
        key: The configuration key
        default: Default value to return if key not found in config

    Returns:
        The boolean value of the configuration or the default value
    """
    if key not in _config_manager._config:
        return default
    return _config_manager.get_boolean(key)


def get_int_config(key: str, default: int = 0) -> int:
    """Get an integer configuration value."""
    return _config_manager.get_int(key, default)


def get_log_level() -> int:
    """
    Get the configured log level as an integer value.

    Returns:
        The log level as an integer (from the logging module)
    """
    log_level_str = get_config("LOG_LEVEL") or "INFO"
    log_level_str = log_level_str.upper()

    log_levels = {
        "CRITICAL": logging.CRITICAL,
        "FATAL": logging.FATAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "WARN": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "NOTSET": logging.NOTSET,
    }

    return log_levels.get(log_level_str, logging.INFO)


def get_excluded_instrumentations() -> list:
    """
    Get the list of excluded instrumentations from configuration.

    Returns:
        A list of instrumentation names to exclude
    """
    exclusions_str = get_config("EXCLUDED_INSTRUMENTATIONS") or ""
    if not exclusions_str:
        return []

    return [name.strip() for name in exclusions_str.split(",") if name.strip()]


def get_safe_logging() -> bool:
    """
    Get whether safe logging is enabled from configuration.

    Returns:
        True if safe logging is enabled, False otherwise
    """
    return get_boolean_config("SAFE_LOGGING")


def get_log_format() -> LogFormatType:
    """
    Get the configured log format type.

    Returns:
        The log format type (DEFAULT or GCP)
    """
    log_format = get_config("LOG_FORMAT") or "default"
    try:
        return LogFormatType(log_format.lower())
    except ValueError:
        return LogFormatType.DEFAULT


def get_typed_config(key: str, value_type: ConfigValueType, default: Any = None) -> Any:
    """
    Get a strongly-typed configuration value.

    Args:
        key: Configuration key
        value_type: Type of value to retrieve
        default: Default value if key not found

    Returns:
        The configuration value converted to the requested type
    """
    return _config_manager.get_typed(key, value_type, default)
