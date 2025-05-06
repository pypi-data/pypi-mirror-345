"""
Logging-specific instrumentation for DTA Observability.
"""

import logging
from typing import Any, Optional

from opentelemetry.instrumentation.logging import LoggingInstrumentor as OTelLoggingInstrumentor
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk.trace import TracerProvider

from dta_observability.instrumentation.base import BaseInstrumentor
from dta_observability.instrumentation.utils import handle_instrumentation_error
from dta_observability.logging.logger import LoggingConfigurator, get_logger


class LoggingInstrumentor(BaseInstrumentor):
    """Handles logging instrumentation with OpenTelemetry integration."""

    _INSTRUMENTED_KEY = "_dta_logging_instrumented"

    def __init__(
        self,
        tracer_provider: Optional[TracerProvider] = None,
        logger_provider: Optional[LoggerProvider] = None,
        meter_provider=None,
        log_level: Optional[int] = logging.INFO,
        safe_logging: bool = True,
    ):
        """Initialize the logging instrumentor."""
        super().__init__(tracer_provider, logger_provider, meter_provider, log_level)
        self.safe_logging = safe_logging
        self.logger = get_logger("dta_observability.instrumentation")

    def _get_library_name(self) -> str:
        """Get the library name."""
        return "logging"

    def instrument(self, app: Any = None) -> bool:
        """
        Set up logging instrumentation with JSON formatting and OpenTelemetry integration.

        Args:
            app: Not used for logging instrumentation, kept for API compatibility

        Returns:
            True if successful, False otherwise
        """

        if self.is_globally_instrumented():
            self.logger.debug("Logging already instrumented")
            return True

        try:

            self._configure_json_formatting()

            self._apply_otel_instrumentation()

            self.set_globally_instrumented()
            return True
        except Exception as e:
            handle_instrumentation_error(self.logger, "logging", e, "instrumentation")
            return False

    def _apply_otel_instrumentation(self) -> None:
        """Apply OpenTelemetry logging instrumentation."""
        try:

            otel_instrumentor = OTelLoggingInstrumentor()
            otel_instrumentor.instrument(
                logger_provider=self.logger_provider,
                tracer_provider=self.tracer_provider,
                log_level=self.log_level,
                set_logging_format=False,
            )
            self.logger.debug("OpenTelemetry logging instrumentation applied")
        except Exception as e:
            if "already instrumented" in str(e).lower():
                self.logger.debug("OpenTelemetry logging was already instrumented")
            else:
                raise

    def _configure_json_formatting(self) -> None:
        """
        Configure consistent JSON formatting for all loggers.

        This ensures that:
        1. All logs use the same formatting
        2. No mixed handlers exist
        3. All loggers use a consistent log level
        """

        log_level = self.log_level or logging.INFO

        self._clear_all_handlers()

        log_handler = LoggingConfigurator.create_handler(
            level=log_level,
            logger_provider=self.logger_provider,
            safe_logging=self.safe_logging,
        )

        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(log_handler)

        LoggingConfigurator.mark_configured()

        self.logger.debug("JSON formatting applied to all loggers")

    def _clear_all_handlers(self) -> None:
        """Remove all handlers from all loggers to prevent mixed logging."""

        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        for name in logging.root.manager.loggerDict:
            logger = logging.getLogger(name)
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
