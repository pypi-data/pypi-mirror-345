"""
DTA Observability instrumentation package.

This package provides automatic instrumentation for common libraries and frameworks.
"""

from dta_observability.instrumentation.auto import configure_instrumentation

__all__ = [
    "configure_instrumentation",
]
