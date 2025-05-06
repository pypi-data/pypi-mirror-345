"""
Celery instrumentation for DTA Observability.

This module provides instrumentation for Celery applications to integrate
with OpenTelemetry for distributed tracing, logging, and metrics.
"""

import logging
from typing import Any, Optional

from dta_observability.core.config import get_log_level
from dta_observability.instrumentation.base import BaseInstrumentor
from dta_observability.instrumentation.utils import configure_framework_logging, handle_instrumentation_error
from dta_observability.logging.logger import get_logger

logger = get_logger(__name__)


class CeleryInstrumentor(BaseInstrumentor):
    """
    Instrument Celery applications for distributed tracing and logging.

    This instrumentor prevents Celery from overriding logging configurations
    and ensures logs are properly captured with trace context.
    """

    _INSTRUMENTED_KEY = "_dta_celery_instrumented"

    def __init__(
        self,
        tracer_provider=None,
        logger_provider=None,
        meter_provider=None,
        log_level=logging.INFO,
        logs_exporter_type=None,
    ):
        """Initialize the Celery instrumentor.

        Args:
            tracer_provider: OpenTelemetry tracer provider
            logger_provider: OpenTelemetry logger provider
            meter_provider: OpenTelemetry meter provider
            log_level: Log level to apply to Celery loggers
            logs_exporter_type: Type of logs exporter to use
        """
        super().__init__(tracer_provider, logger_provider, meter_provider, log_level)
        self.logger = get_logger("dta_observability.instrumentation")
        self.logs_exporter_type = logs_exporter_type
        self.tracer_provider = tracer_provider
        self.logger_provider = logger_provider
        self.meter_provider = meter_provider
        log_level = get_log_level()

    def _get_library_name(self) -> str:
        """Get the library name for instrumentation."""
        return "celery"

    def instrument(self, app: Any = None) -> bool:
        """Instrument a Celery application.

        Args:
            app: Optional Celery app instance to instrument

        Returns:
            bool: True if instrumentation was successful
        """
        try:

            if app is not None and hasattr(app, self._INSTRUMENTED_KEY):
                self.logger.debug("Celery app already instrumented, skipping")
                return True

            from opentelemetry.instrumentation.celery import CeleryInstrumentor as OTelCeleryInstrumentor

            OTelCeleryInstrumentor(
                tracer_provider=self.tracer_provider,
                logger_provider=self.logger_provider,
                meter_provider=self.meter_provider,
                log_level=self.log_level,
            ).instrument()

            self.instrument_celery(app, self.logger_provider, self.tracer_provider, self.meter_provider, self.log_level)

            if app is not None:
                setattr(app, self._INSTRUMENTED_KEY, True)
                self.register_app(app)
                self.logger.debug(f"Celery app instrumented: {app}")

            self.logger.debug("Celery instrumentation complete")
            return True

        except Exception as e:
            handle_instrumentation_error(self.logger, "Celery", e, "instrumentation")
            return False

    def uninstrument(self, app: Optional[Any] = None) -> None:
        """Remove Celery instrumentation.

        Args:
            app: Optional Celery app to uninstrument
        """

        if app is not None:
            if hasattr(app, self._INSTRUMENTED_KEY):
                delattr(app, self._INSTRUMENTED_KEY)
            if hasattr(app, "_dta_instrumentor"):
                delattr(app, "_dta_instrumentor")
            self.logger.debug(f"Uninstrumented Celery app: {app}")

    def _setup_basic_handlers(
        self, celery_app: Any, logger_provider: Any, tracer_provider: Any, meter_provider: Any, log_level: Any
    ) -> None:
        """Setup minimal handlers for telemetry."""
        try:

            celery_app.conf.worker_hijack_root_logger = False

            from celery.signals import (  # type: ignore
                setup_logging,
                worker_process_init,
            )

            @setup_logging.connect(weak=False)
            def on_setup_logging(**kwargs):
                """
                Prevent Celery from setting up its own logging.
                This ensures our OpenTelemetry logging is preserved.
                """

                from dta_observability.logging.logger import LoggingConfigurator

                try:
                    configure_framework_logging(log_level=log_level)

                    log_handler = LoggingConfigurator.create_handler(
                        level=log_level, logger_provider=logger_provider, safe_logging=True
                    )

                    LoggingConfigurator.configure_root_logger(log_level, log_handler, replace_existing=False)

                    print("DTA Observability: Logging reconfigured in setup_logging phase")
                except Exception as e:
                    print(f"Error in setup_logging: {e}")

                return True

            @worker_process_init.connect(weak=False)
            def on_worker_process_init(**kwargs):
                """Reinitialize logging when worker process starts."""

                from dta_observability.logging.logger import LoggingConfigurator

                try:
                    configure_framework_logging(log_level=log_level)
                    log_handler = LoggingConfigurator.create_handler(
                        level=log_level, logger_provider=logger_provider, safe_logging=True
                    )

                    LoggingConfigurator.configure_root_logger(log_level, log_handler, replace_existing=False)

                    LoggingConfigurator.mark_configured()

                except Exception as e:

                    print(f"Error reinitializing logging in worker: {e}")

        except Exception as e:
            logger.error("Failed to set up Celery handlers: %s", e)

    def instrument_celery(
        self, celery_app: Any, logger_provider: Any, tracer_provider: Any, meter_provider: Any, log_level: Any
    ) -> None:
        """
        Instrument a Celery application with DTA Observability.

        Args:
            celery_app: The Celery application instance
        """
        if not celery_app:
            return

        if getattr(celery_app, "_dta_celery_helpers_instrumented", False):
            logger.debug("Celery app already instrumented by celery_helpers, skipping")
            return

        self._setup_basic_handlers(celery_app, logger_provider, tracer_provider, meter_provider, log_level)

        setattr(celery_app, "_dta_celery_helpers_instrumented", True)

        logger.info("Celery app instrumentation completed")
