"""
Core functionality for DTA Observability.
"""

from dta_observability.core.config import get_config
from dta_observability.core.telemetry import init_telemetry

__all__ = ["init_telemetry", "get_config"]
