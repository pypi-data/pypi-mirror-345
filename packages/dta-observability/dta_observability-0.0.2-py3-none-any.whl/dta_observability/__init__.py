"""
DTA Observability - A lightweight wrapper around OpenTelemetry core APIs.
"""

__version__ = "0.1.0"

from dta_observability.core.span import (
    traced,
)
from dta_observability.core.telemetry import init_telemetry
from dta_observability.logging.logger import get_logger

__all__ = ["init_telemetry", "get_logger", "traced"]
