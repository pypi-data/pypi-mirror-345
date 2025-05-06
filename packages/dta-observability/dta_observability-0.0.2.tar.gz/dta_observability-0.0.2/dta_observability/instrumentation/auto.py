"""
Auto-instrumentation for DTA Observability.
"""

import importlib
from typing import Any, Dict, List, Optional, Type

from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace import TracerProvider

from dta_observability.instrumentation._create_instrumentors import (
    create_httpx_instrumentor,
    create_requests_instrumentor,
)
from dta_observability.instrumentation.base import BaseInstrumentor
from dta_observability.instrumentation.detector import InstrumentationMap, PackageDetector
from dta_observability.instrumentation.instrumentors import (
    CeleryInstrumentor,
    FastAPIInstrumentor,
    FlaskInstrumentor,
    LoggingInstrumentor,
    SystemMetricsInstrumentor,
)
from dta_observability.instrumentation.registry import instrumentation_registry
from dta_observability.instrumentation.utils import handle_instrumentation_error
from dta_observability.logging.logger import get_logger


class AutoInstrumentor:
    """
    Manages automatic instrumentation of libraries.
    """

    INSTRUMENTOR_REGISTRY: Dict[str, Type[BaseInstrumentor]] = {
        "flask": FlaskInstrumentor,
        "fastapi": FastAPIInstrumentor,
        "celery": CeleryInstrumentor,
    }

    def __init__(
        self,
        tracer_provider: Optional[TracerProvider] = None,
        meter_provider: Optional[MeterProvider] = None,
        excluded_libraries: Optional[List[str]] = None,
        logger_provider: Optional[LoggerProvider] = None,
        log_level: Optional[int] = None,
        logs_exporter_type: Optional[str] = None,
    ):
        """
        Initialize the auto-instrumentor.

        Args:
            tracer_provider: The tracer provider to use for instrumentation
            meter_provider: The meter provider to use for metrics
            excluded_libraries: List of library names to exclude from instrumentation
            logger_provider: The logger provider to use for instrumentation
            log_level: The log level to use for instrumentation
            logs_exporter_type: Optional logs exporter type to use
        """
        self.tracer_provider = tracer_provider
        self.logger_provider = logger_provider
        self.meter_provider = meter_provider
        self.log_level = log_level
        self.logs_exporter_type = logs_exporter_type
        self.excluded_libraries = set(excluded_libraries or [])
        self.instrumented_libraries: List[str] = []
        self.logger = get_logger("dta_observability.instrumentation")

    def instrument_specific_app(self, library_name: str, app: Any) -> bool:
        """
        Instrument a specific application instance.

        Args:
            library_name: The library name (e.g., "flask", "fastapi")
            app: The application instance to instrument

        Returns:
            True if instrumentation was successful, False otherwise
        """
        if library_name in self.excluded_libraries:
            return False

        if library_name not in self.INSTRUMENTOR_REGISTRY:
            self.logger.debug(f"No instrumentor found for {library_name}")
            return False

        try:

            instrumentor_class = self.INSTRUMENTOR_REGISTRY[library_name]

            if library_name == "celery":
                from dta_observability.instrumentation.instrumentors.celery import CeleryInstrumentor

                result = CeleryInstrumentor(
                    tracer_provider=self.tracer_provider,
                    logger_provider=self.logger_provider,
                    meter_provider=self.meter_provider,
                    log_level=self.log_level,
                    logs_exporter_type=self.logs_exporter_type,
                ).instrument(app)

                if result:
                    self.instrumented_libraries.append(library_name)
                    self.excluded_libraries.add(library_name)

                return result

            elif library_name == "flask":
                from dta_observability.instrumentation.instrumentors.flask import FlaskInstrumentor

                result = FlaskInstrumentor(
                    tracer_provider=self.tracer_provider,
                    logger_provider=self.logger_provider,
                    meter_provider=self.meter_provider,
                    log_level=self.log_level,
                    logs_exporter_type=self.logs_exporter_type,
                ).instrument(app)

                if result:
                    self.instrumented_libraries.append(library_name)
                    self.excluded_libraries.add(library_name)

                return result

            elif library_name == "fastapi":
                from dta_observability.instrumentation.instrumentors.fastapi import FastAPIInstrumentor

                result = FastAPIInstrumentor(
                    tracer_provider=self.tracer_provider,
                    logger_provider=self.logger_provider,
                    meter_provider=self.meter_provider,
                    log_level=self.log_level,
                    logs_exporter_type=self.logs_exporter_type,
                ).instrument(app)

                if result:
                    self.instrumented_libraries.append(library_name)
                    self.excluded_libraries.add(library_name)

                return result

            instrumentor = instrumentor_class(
                tracer_provider=self.tracer_provider,
                logger_provider=self.logger_provider,
                meter_provider=self.meter_provider,
                log_level=self.log_level,
            )

            result = instrumentor.instrument(app)

            if result:
                self.instrumented_libraries.append(library_name)
                self.excluded_libraries.add(library_name)

            return result

        except Exception as e:
            handle_instrumentation_error(self.logger, library_name, e, "specific app instrumentation")
            return False


def _instrument_library(instrumentor: AutoInstrumentor, library_name: str) -> bool:
    """
    Instrument a specific library by name.

    Args:
        instrumentor: The AutoInstrumentor instance
        library_name: The name of the library to instrument

    Returns:
        True if instrumentation was successful, False otherwise
    """
    logger = get_logger("dta_observability.instrumentation")

    if instrumentation_registry.is_globally_instrumented(library_name):
        logger.debug(f"Library {library_name} already globally instrumented, skipping")
        if library_name not in instrumentor.instrumented_libraries:
            instrumentor.instrumented_libraries.append(library_name)
        return True

    module_path = InstrumentationMap.get_module_path(library_name)
    if not module_path or not (
        PackageDetector.is_available(library_name) and PackageDetector.is_available(module_path)
    ):
        logger.debug(f"Library {library_name} or its instrumentation is not available, skipping")
        return False

    try:
        otel_instrumentor = _create_otel_instrumentor(library_name)
        if not otel_instrumentor:
            return False

        kwargs: Dict[str, Any] = {}
        if instrumentor.tracer_provider is not None:
            kwargs["tracer_provider"] = instrumentor.tracer_provider

        if instrumentor.log_level is not None:
            kwargs["log_level"] = instrumentor.log_level

        try:
            otel_instrumentor.instrument(**kwargs)
            instrumentation_registry.set_globally_instrumented(library_name)
            instrumentor.instrumented_libraries.append(library_name)
            return True
        except Exception as e:
            if "already instrumented" in str(e).lower():
                instrumentation_registry.set_globally_instrumented(library_name)
                instrumentor.instrumented_libraries.append(library_name)
                logger.debug(f"Library {library_name} was already instrumented")
                return True
            raise

    except Exception as e:
        handle_instrumentation_error(logger, library_name, e, "auto-instrumentation")
        return False


def _create_otel_instrumentor(library_name: str) -> Optional[Any]:
    """
    Create an OpenTelemetry instrumentor instance dynamically.

    Args:
        library_name: The name of the library to create an instrumentor for

    Returns:
        An instrumentor instance or None if creation failed
    """
    try:

        module_path = InstrumentationMap.get_module_path(library_name)
        if not module_path:
            return None

        module = importlib.import_module(module_path)
        class_name = InstrumentationMap.get_instrumentor_class_name(library_name)
        return getattr(module, class_name)()
    except (ImportError, AttributeError) as e:
        logger = get_logger("dta_observability.instrumentation")
        logger.debug(f"Could not create instrumentor for {library_name}: {e}")
        return None


def configure_instrumentation(
    tracer_provider: Optional[TracerProvider] = None,
    excluded_instrumentations: Optional[List[str]] = None,
    flask_app: Optional[Any] = None,
    fastapi_app: Optional[Any] = None,
    celery_app: Optional[Any] = None,
    logger_provider: Optional[LoggerProvider] = None,
    meter_provider: Optional[MeterProvider] = None,
    log_level: Optional[int] = None,
    safe_logging: bool = True,
    enable_logging_instrumentation: Optional[bool] = True,
    enable_system_metrics: Optional[bool] = None,
    system_metrics_config: Optional[dict] = None,
    logs_exporter_type: Optional[str] = None,
) -> None:
    """
    Configure auto-instrumentation for common libraries.

    Args:
        tracer_provider: The tracer provider to use for instrumentation.
        excluded_instrumentations: List of instrumentation names to exclude.
        flask_app: Optional Flask application instance to instrument directly.
        fastapi_app: Optional FastAPI application instance to instrument directly.
        celery_app: Optional Celery application instance to instrument directly.
        logger_provider: Optional logger provider for logging instrumentation.
        meter_provider: Optional meter provider for metrics instrumentation.
        log_level: The log level to use for instrumentation.
        safe_logging: Whether to enable safe logging with complex data type handling.
        enable_logging_instrumentation: Whether to enable logging instrumentation.
        enable_system_metrics: Whether to enable system metrics collection.
        system_metrics_config: Optional configuration for system metrics collection.
        logs_exporter_type: Optional logs exporter type to use.
    """

    excluded_instrumentations = excluded_instrumentations or []

    logger = get_logger("dta_observability.instrumentation")

    instrumentor = AutoInstrumentor(
        tracer_provider=tracer_provider,
        excluded_libraries=excluded_instrumentations,
        logger_provider=logger_provider,
        meter_provider=meter_provider,
        log_level=log_level,
        logs_exporter_type=logs_exporter_type,
    )

    for library_name in InstrumentationMap.LIBRARIES:
        if library_name not in instrumentor.excluded_libraries:
            _instrument_library(instrumentor, library_name)

    system_metrics_instrumentor = SystemMetricsInstrumentor(
        tracer_provider=tracer_provider,
        meter_provider=meter_provider,
        config=system_metrics_config,
        logger=logger,
    )
    if system_metrics_instrumentor.instrument():
        logger.debug("System metrics instrumentation enabled")
    else:
        logger.warning("Failed to enable system metrics instrumentation")

    if flask_app:
        instrumentor.instrument_specific_app("flask", flask_app)

    if fastapi_app:
        instrumentor.instrument_specific_app("fastapi", fastapi_app)

    if celery_app:
        instrumentor.instrument_specific_app("celery", celery_app)

    try:
        create_requests_instrumentor()
        create_httpx_instrumentor()
    except Exception as e:
        logger.warning(f"Failed to instrument requests and httpx: {e}")

    logging_instrumentor = LoggingInstrumentor(
        tracer_provider=tracer_provider,
        logger_provider=logger_provider,
        log_level=log_level,
        safe_logging=safe_logging,
    )
    if logging_instrumentor.instrument():
        logger.debug("Logging instrumentation enabled")
    else:
        logger.warning("Failed to enable logging instrumentation")

    if instrumentor.instrumented_libraries:
        logger.debug(f"Auto-instrumented libraries: {', '.join(instrumentor.instrumented_libraries)}")
    else:
        logger.debug("No libraries were auto-instrumented")
