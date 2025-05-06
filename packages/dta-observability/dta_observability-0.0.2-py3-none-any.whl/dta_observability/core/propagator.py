"""
Context propagation configuration for DTA Observability.
"""

from enum import Enum, auto
from typing import Any, Dict, List, Optional

from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.cloud_trace_propagator import CloudTraceFormatPropagator
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from dta_observability.core.config import get_config


class PropagatorType(Enum):
    """Types of supported context propagators."""

    W3C = auto()
    BAGGAGE = auto()
    GCP = auto()


class PropagatorRegistry:
    """Registry of available propagator types and their factories."""

    NAME_ALIASES: Dict[str, PropagatorType] = {
        "w3c": PropagatorType.W3C,
        "tracecontext": PropagatorType.W3C,
        "baggage": PropagatorType.BAGGAGE,
        "gcp": PropagatorType.GCP,
        "gcp_trace": PropagatorType.GCP,
    }

    FACTORIES: Dict[PropagatorType, Any] = {
        PropagatorType.W3C: TraceContextTextMapPropagator,
        PropagatorType.BAGGAGE: W3CBaggagePropagator,
        PropagatorType.GCP: CloudTraceFormatPropagator,
    }

    @classmethod
    def get_propagator_type(cls, name: str) -> Optional[PropagatorType]:
        """Get propagator type from name."""
        return cls.NAME_ALIASES.get(name.strip().lower())

    @classmethod
    def create_propagator(cls, prop_type: PropagatorType) -> Any:
        """Create a propagator instance from type."""
        factory = cls.FACTORIES.get(prop_type)
        if factory:
            return factory()
        return None


def get_propagators(propagator_names: str) -> List[Any]:
    """
    Get propagator instances from a comma-separated list of names.

    Args:
        propagator_names: Comma-separated list of propagator names.

    Returns:
        List of propagator instances.
    """
    propagators = []
    names = [name.strip().lower() for name in propagator_names.split(",")]

    for name in names:
        prop_type = PropagatorRegistry.get_propagator_type(name)
        if prop_type:
            propagator = PropagatorRegistry.create_propagator(prop_type)
            if propagator:
                propagators.append(propagator)

    return propagators


def configure_propagation() -> None:
    """
    Configure global propagation with W3C and GCP propagators by default.
    """

    names = get_config("PROPAGATORS") or get_config("OTEL_PROPAGATORS") or "tracecontext,baggage,gcp_trace"

    propagators = get_propagators(names)

    if not propagators:
        propagators = [
            PropagatorRegistry.create_propagator(PropagatorType.W3C),
            PropagatorRegistry.create_propagator(PropagatorType.BAGGAGE),
        ]

    composite = CompositePropagator(propagators)
    set_global_textmap(composite)


def configure_specific_propagation(propagator_list: List[str]) -> None:
    """
    Configure global propagation with specific propagators.

    Args:
        propagator_list: List of propagator names to configure
    """
    if propagator_list:
        propagator_names = ",".join(propagator_list)
        names = propagator_names

        propagators = get_propagators(names)

        if not propagators:
            propagators = [
                PropagatorRegistry.create_propagator(PropagatorType.W3C),
                PropagatorRegistry.create_propagator(PropagatorType.BAGGAGE),
            ]

        composite = CompositePropagator(propagators)
        set_global_textmap(composite)
