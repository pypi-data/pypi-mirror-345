"""
System metrics instrumentation using OpenTelemetry.
"""

import os
from typing import Any, Dict, List, Optional, Union

from dta_observability.core.config import get_boolean_config, get_config
from dta_observability.instrumentation.base import BaseInstrumentor
from dta_observability.logging.logger import get_logger


class SystemMetricsInstrumentor(BaseInstrumentor):
    """
    Instrumentor for system metrics collection.

    Collects system (CPU, memory, network) and process metrics using OpenTelemetry.
    """

    def __init__(
        self,
        tracer_provider=None,
        logger_provider=None,
        meter_provider=None,
        log_level=None,
        config: Optional[Dict[str, Union[List[str], None]]] = None,
        logger: Any = None,
    ):
        """
        Initialize the system metrics instrumentor.

        Args:
            tracer_provider: Optional tracer provider for trace context
            logger_provider: Optional logger provider for logs
            meter_provider: Optional meter provider for metrics
            log_level: Optional log level for logging
            config: Optional configuration to specify which metrics to collect
            logger: Optional logger instance
        """
        super().__init__(tracer_provider, logger_provider, meter_provider, log_level)
        self.config = config
        self._instrumentor: Any = None
        self._system_metrics_enabled = get_boolean_config("SYSTEM_METRICS_ENABLED", default=True)

        if logger:
            self.logger = logger
        elif not hasattr(self, "logger") or self.logger is None:
            self.logger = get_logger("dta_observability.instrumentation")

        self._hostname = os.environ.get("HOSTNAME", "unknown")

    def _get_library_name(self) -> str:
        """Get the name of the library being instrumented."""
        return "system_metrics"

    def _get_metrics_config(self) -> Dict[str, Any]:
        """
        Get metrics configuration based on system metrics enabled setting.

        Returns:
            Configuration dict with appropriate metrics
        """
        try:
            from opentelemetry.instrumentation.system_metrics import _DEFAULT_CONFIG

            if self.config is not None:
                return self.config

            if not self._system_metrics_enabled:
                return {}

            metrics_config = {
                k: v
                for k, v in _DEFAULT_CONFIG.items()
                if k.startswith("process") and not k.startswith("process.runtime")
            }

            exporter_type = get_config("METRICS_EXPORTER_TYPE") or get_config("EXPORTER_TYPE")
            if exporter_type == "gcp":
                self.logger.debug(
                    "Using GCP-compatible metrics configuration - removing process.cpu.time to avoid rate limiting"
                )
                metrics_config.pop("process.cpu.time", None)

            return metrics_config
        except ImportError:
            self.logger.warning("Could not import default system metrics config")
            return {}

    def _import_instrumentor(self) -> bool:
        """
        Import the OpenTelemetry system metrics instrumentor.

        Returns:
            True if import was successful, False otherwise
        """
        try:
            from opentelemetry.instrumentation.system_metrics import (
                SystemMetricsInstrumentor as OTelSystemMetricsInstrumentor,
            )

            metrics_config = self._get_metrics_config()

            if not metrics_config:
                return False

            labels = {"hostname": str(self._hostname), "process_id": str(os.getpid())}

            if "process.cpu.time" in metrics_config:
                metrics_config.pop("process.cpu.time", None)

            self._instrumentor = OTelSystemMetricsInstrumentor(config=metrics_config, labels=labels)
            return True

        except ImportError:
            self.logger.warning(
                "opentelemetry-instrumentation-system-metrics package not found. "
                "Install it with: pip install opentelemetry-instrumentation-system-metrics"
            )
            return False

    def instrument(self, app: Any = None) -> bool:
        """
        Instrument system metrics collection.

        Returns:
            True if instrumentation was successful, False otherwise
        """
        if not self._system_metrics_enabled:
            self.logger.debug("System metrics collection disabled by configuration")
            return False

        if not self._instrumentor and not self._import_instrumentor():
            self.logger.error("Failed to import system metrics instrumentor")
            return False

        try:
            self._instrumentor.instrument(meter_provider=self.meter_provider)
            return True
        except Exception as e:
            self.logger.error(f"Failed to instrument system metrics: {e}")
            return False
