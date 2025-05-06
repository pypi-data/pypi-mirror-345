"""
Telemetry initialization for DTA Observability.

This module provides functions and classes for initializing and configuring
OpenTelemetry for distributed tracing, logging, and metrics collection.
"""

import logging
import os
import sys
import traceback
from typing import Any, List, Literal, Optional, Union

from opentelemetry import _logs, metrics, trace
from opentelemetry.exporter.cloud_monitoring import CloudMonitoringMetricsExporter
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogExporter
from opentelemetry.sdk.error_handler import GlobalErrorHandler
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.semconv.resource import ResourceAttributes

from dta_observability.core.config import (
    LogFormatType,
    get_boolean_config,
    get_config,
    get_excluded_instrumentations,
    get_int_config,
    get_log_format,
    get_log_level,
    get_safe_logging,
)
from dta_observability.core.propagator import configure_propagation, configure_specific_propagation
from dta_observability.instrumentation.auto import configure_instrumentation
from dta_observability.logging.logger import DTAErrorHandler, LoggingConfigurator, get_logger
from dta_observability.resources.detector import detect_resources

ExporterType = Literal["otlp", "console", "gcp"]


class ExporterFactory:
    """Factory for creating OpenTelemetry exporters."""

    @staticmethod
    def create_trace_exporter(exporter_type: str, endpoint: str, insecure: bool) -> Any:
        """Create a trace exporter based on configuration.

        Args:
            exporter_type: Type of exporter (otlp, console, gcp)
            endpoint: OTLP endpoint URL
            insecure: Whether to use insecure connection

        Returns:
            Configured trace exporter
        """
        logger = get_logger("dta_observability.telemetry")

        if exporter_type == "console":
            return ConsoleSpanExporter()
        elif exporter_type == "gcp":
            try:
                project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

                exporter = CloudTraceSpanExporter(project_id=project_id, resource_regex=r".*")
                logger.debug(
                    f"GCP Cloud Trace exporter configured for project: {project_id or 'auto-detected'} with all resource attributes"
                )
                return exporter
            except (ImportError, Exception) as e:
                logger.warning(f"Failed to configure GCP Cloud Trace exporter: {e}")
                return ConsoleSpanExporter()
        else:
            return OTLPSpanExporter(endpoint=endpoint, insecure=insecure)

    @staticmethod
    def create_metric_exporter(exporter_type: str, endpoint: str, insecure: bool) -> Any:
        """Create a metric exporter based on configuration.

        Args:
            exporter_type: Type of exporter (otlp, console, gcp)
            endpoint: OTLP endpoint URL
            insecure: Whether to use insecure connection

        Returns:
            Configured metric exporter
        """
        logger = get_logger("dta_observability.telemetry")

        if exporter_type == "console":
            return ConsoleMetricExporter()
        elif exporter_type == "gcp":
            try:
                exporter = CloudMonitoringMetricsExporter(add_unique_identifier=True, prefix="workload.googleapis.com")
                logger.debug("GCP Cloud Monitoring exporter configured")
                return exporter
            except (ImportError, Exception) as e:
                logger.warning(f"Failed to configure GCP Cloud Monitoring exporter: {e}")
                return ConsoleMetricExporter()
        else:
            return OTLPMetricExporter(endpoint=endpoint, insecure=insecure)

    @staticmethod
    def create_log_exporter(exporter_type: str, endpoint: str, insecure: bool) -> Any:
        """Create a log exporter based on configuration.

        Args:
            exporter_type: Type of exporter (otlp, console, gcp)
            endpoint: OTLP endpoint URL
            insecure: Whether to use insecure connection

        Returns:
            Configured log exporter
        """

        if exporter_type == "console":
            return ConsoleLogExporter()
        else:
            return OTLPLogExporter(endpoint=endpoint, insecure=insecure)


class TelemetryInitializer:
    """Initializes and configures OpenTelemetry components."""

    def __init__(
        self,
        service_name: Optional[str] = None,
        service_version: Optional[str] = None,
        resource_attributes: Optional[Resource] = None,
        log_level: int = logging.INFO,
        safe_logging: bool = True,
        log_format: LogFormatType = LogFormatType.DEFAULT,
        otlp_endpoint: Optional[str] = None,
        otlp_insecure: Optional[bool] = None,
        batch_export_delay_ms: Optional[int] = None,
        enable_resource_detectors: bool = True,
        exporter_type: ExporterType = "otlp",
        traces_exporter_type: Optional[ExporterType] = None,
        metrics_exporter_type: Optional[ExporterType] = None,
        logs_exporter_type: Optional[ExporterType] = None,
        enable_traces: bool = True,
        enable_metrics: bool = True,
        enable_logs: bool = True,
        enable_system_metrics: bool = True,
    ):
        """Initialize telemetry configuration.

        Args:
            service_name: Name of the service
            service_version: Version of the service
            resource_attributes: Additional resource attributes
            log_level: Logging level
            safe_logging: Whether to handle complex objects in logs
            log_format: Format for logs (DEFAULT or GCP)
            otlp_endpoint: OTLP endpoint URL
            otlp_insecure: Whether to use insecure connection
            batch_export_delay_ms: Delay between batch exports
            enable_resource_detectors: Whether to use resource detection
            exporter_type: Default exporter type
            traces_exporter_type: Specific exporter for traces
            metrics_exporter_type: Specific exporter for metrics
            logs_exporter_type: Specific exporter for logs
            enable_traces: Whether to enable tracing
            enable_metrics: Whether to enable metrics
            enable_logs: Whether to enable logs
            enable_system_metrics: Whether to enable system metrics
        """

        self.service_name = service_name
        self.service_version = service_version
        self.resource_attributes = resource_attributes
        self.log_level = log_level
        self.safe_logging = safe_logging
        self.log_format = log_format
        self.logger = get_logger("dta_observability.telemetry")

        self.exporter_config = {
            "endpoint": otlp_endpoint or get_config("EXPORTER_OTLP_ENDPOINT") or "http://localhost:4317",
            "insecure": otlp_insecure if otlp_insecure is not None else get_boolean_config("EXPORTER_OTLP_INSECURE"),
            "batch_delay_ms": batch_export_delay_ms or get_int_config("BATCH_EXPORT_SCHEDULE_DELAY", 120000),
            "exporter_type": exporter_type,
            "traces_exporter_type": traces_exporter_type or get_config("TRACES_EXPORTER_TYPE") or exporter_type,
            "metrics_exporter_type": metrics_exporter_type or get_config("METRICS_EXPORTER_TYPE") or exporter_type,
            "logs_exporter_type": logs_exporter_type or get_config("LOGS_EXPORTER_TYPE") or exporter_type,
            "enable_traces": enable_traces,
            "enable_metrics": enable_metrics,
            "enable_logs": enable_logs,
        }

    def configure_tracing(self, resource: Resource) -> Optional[TracerProvider]:
        """Configure and initialize trace provider.

        Returns:
            TracerProvider if tracing is enabled, None otherwise
        """
        if not self.exporter_config["enable_traces"]:
            return None

        tracer_provider = TracerProvider(resource=resource)

        exporter_type = str(self.exporter_config["traces_exporter_type"])
        endpoint = str(self.exporter_config["endpoint"])
        insecure = bool(self.exporter_config["insecure"])
        exporter = ExporterFactory.create_trace_exporter(exporter_type, endpoint, insecure)

        if exporter_type == "gcp":

            span_processor = BatchSpanProcessor(
                exporter, max_export_batch_size=256, schedule_delay_millis=120000, max_queue_size=2048
            )
        else:
            span_processor = BatchSpanProcessor(exporter)

        tracer_provider.add_span_processor(span_processor)

        return tracer_provider

    def configure_metrics(self, resource: Resource) -> Optional[MeterProvider]:
        """Configure and initialize meter provider.

        Returns:
            MeterProvider if metrics are enabled, None otherwise
        """
        if not self.exporter_config["enable_metrics"]:
            return None

        exporter_type = str(self.exporter_config["metrics_exporter_type"])
        endpoint = str(self.exporter_config["endpoint"])
        insecure = bool(self.exporter_config["insecure"])
        exporter = ExporterFactory.create_metric_exporter(exporter_type, endpoint, insecure)

        export_interval = int(self.exporter_config["batch_delay_ms"])
        if exporter_type == "gcp":

            gcp_interval = 120000
            self.logger.debug(f"Adjusting GCP metrics export interval from {export_interval}ms to {gcp_interval}ms")
            export_interval = gcp_interval

        metrics_reader = PeriodicExportingMetricReader(exporter, export_interval_millis=float(export_interval))

        meter_provider = MeterProvider(resource=resource, metric_readers=[metrics_reader])

        self.logger.debug("Metrics provider configured")
        return meter_provider

    def configure_logging(self, resource: Resource) -> Optional[LoggerProvider]:
        """Configure logging with trace context.

        Returns:
            LoggerProvider if OTLP logging is enabled, None otherwise
        """

        is_gcp_format = self.log_format == LogFormatType.GCP

        if is_gcp_format:

            if not LoggingConfigurator.is_configured():
                LoggingConfigurator.configure_gcp_logging(log_level=self.log_level, safe_logging=self.safe_logging)

                self.logger.debug(f"GCP logging format enabled for service: {self.service_name}")

            return None

        try:

            logger_provider = LoggerProvider(resource=resource)

            exporter_type = str(self.exporter_config["logs_exporter_type"])
            endpoint = str(self.exporter_config["endpoint"])
            insecure = bool(self.exporter_config["insecure"])
            exporter = ExporterFactory.create_log_exporter(exporter_type, endpoint, insecure)

            log_destination = (
                "console" if exporter_type == "console" else f"OTLP endpoint ({self.exporter_config['endpoint']})"
            )

            logger_provider.add_log_record_processor(
                BatchLogRecordProcessor(
                    exporter,
                    max_export_batch_size=512,
                    schedule_delay_millis=1000,
                    max_queue_size=10000,
                )
            )

            handler = LoggingConfigurator.create_handler(
                level=self.log_level, logger_provider=logger_provider, safe_logging=self.safe_logging
            )

            LoggingConfigurator.mark_configured()

            self.logger.debug(f"OpenTelemetry logging enabled - logs sent to {log_destination}")
            return logger_provider

        except Exception as e:

            print(f"Warning: Failed to initialize OpenTelemetry logging: {e}", file=sys.stderr)

            handler = logging.StreamHandler()
            handler.setFormatter(LoggingConfigurator.create_formatter(safe_logging=self.safe_logging))
            handler.setLevel(self.log_level)
            setattr(handler, "_dta_otel_handler", True)

            return None

    def _reset_logging_config(self) -> None:
        """Reset existing logging configuration."""

        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
            handler.close()

        logging.captureWarnings(True)

        for name in logging.root.manager.loggerDict:
            logger = logging.getLogger(name)
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)

    def setup_exception_handling(self) -> None:
        """Configure global exception handling to track unhandled exceptions."""

        original_excepthook = sys.excepthook

        def global_exception_hook(exc_type: type, exc_value: BaseException, exc_traceback: Any) -> None:
            """Global exception hook for unhandled exceptions.

            Args:
                exc_type: Exception type
                exc_value: Exception value
                exc_traceback: Exception traceback
            """
            with GlobalErrorHandler():
                try:

                    current_span = trace.get_current_span()
                    span_context = current_span.get_span_context() if current_span else None

                    formatted_traceback = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

                    log_extra = {
                        "error_type": exc_type.__name__,
                        "error_message": str(exc_value),
                    }

                    if span_context:

                        log_extra.update(
                            {
                                "trace_id": str(span_context.trace_id),
                                "span_id": str(span_context.span_id),
                            }
                        )

                    logger = get_logger("dta_observability.error")
                    logger.error(
                        f"Unhandled exception caught: {exc_value}\n{formatted_traceback}",
                        extra=log_extra,
                    )

                    if isinstance(exc_value, Exception):
                        from dta_observability.core.span import mark_error_event

                        mark_error_event(exc_value, False)

                        dta_handler = DTAErrorHandler()
                        dta_handler.handle(exc_value)
                except Exception:

                    pass

            original_excepthook(exc_type, exc_value, exc_traceback)

        sys.excepthook = global_exception_hook


def _resolve_log_level(log_level: Optional[Union[int, str]]) -> int:
    """Resolve logging level from various input types.

    Args:
        log_level: Log level as int, string, or None

    Returns:
        Resolved log level as integer
    """

    if log_level is None:
        return get_log_level()

    if isinstance(log_level, str):
        try:
            return int(log_level)
        except ValueError:

            level_map = {
                "debug": logging.DEBUG,
                "info": logging.INFO,
                "warning": logging.WARNING,
                "error": logging.ERROR,
                "critical": logging.CRITICAL,
            }
            return level_map.get(log_level.lower(), logging.INFO)

    return log_level


def init_telemetry(
    service_name: Optional[str] = None,
    service_version: Optional[str] = None,
    service_instance_id: Optional[str] = None,
    resource_attributes: Optional[Resource] = None,
    configure_auto_instrumentation: Optional[bool] = None,
    log_level: Optional[Union[int, str]] = None,
    log_format: Optional[Union[str, LogFormatType]] = None,
    flask_app: Optional[Any] = None,
    fastapi_app: Optional[Any] = None,
    celery_app: Optional[Any] = None,
    safe_logging: Optional[bool] = None,
    excluded_instrumentations: Optional[List[str]] = None,
    otlp_endpoint: Optional[str] = None,
    otlp_insecure: Optional[bool] = None,
    batch_export_delay_ms: Optional[int] = None,
    enable_resource_detectors: Optional[bool] = None,
    enable_logging_instrumentation: Optional[bool] = None,
    propagators: Optional[str] = None,
    exporter_type: Optional[ExporterType] = None,
    traces_exporter_type: Optional[ExporterType] = None,
    metrics_exporter_type: Optional[ExporterType] = None,
    logs_exporter_type: Optional[ExporterType] = None,
    enable_traces: Optional[bool] = None,
    enable_metrics: Optional[bool] = None,
    enable_logs: Optional[bool] = None,
    enable_system_metrics: Optional[bool] = None,
    system_metrics_config: Optional[dict] = None,
) -> None:
    """Initialize telemetry with sensible defaults.

    Args:
        service_name: Name of the service
        service_version: Version of the service
        service_instance_id: Unique instance ID
        resource_attributes: Additional resource attributes
        configure_auto_instrumentation: Whether to configure auto-instrumentation
        log_level: Logging level
        log_format: Format for logs (default or gcp)
        flask_app: Flask app to instrument
        fastapi_app: FastAPI app to instrument
        celery_app: Celery app to instrument
        safe_logging: Whether to handle complex objects in logs
        excluded_instrumentations: List of instrumentations to exclude
        otlp_endpoint: OTLP endpoint URL
        otlp_insecure: Whether to use insecure connection
        batch_export_delay_ms: Delay between batch exports
        enable_resource_detectors: Whether to detect resources
        enable_logging_instrumentation: Whether to instrument logging
        propagators: Context propagators to use
        exporter_type: Default exporter type
        traces_exporter_type: Specific exporter for traces
        metrics_exporter_type: Specific exporter for metrics
        logs_exporter_type: Specific exporter for logs
        enable_traces: Whether to enable tracing
        enable_metrics: Whether to enable metrics
        enable_logs: Whether to enable logs
        enable_system_metrics: Whether to enable system metrics
        system_metrics_config: Configuration for system metrics
    """

    configure_propagation()

    logger = get_logger("dta_observability.telemetry")

    actual_log_level = _resolve_log_level(log_level)
    actual_safe_logging = safe_logging if safe_logging is not None else get_safe_logging()

    actual_log_format = log_format
    if isinstance(actual_log_format, str) and actual_log_format:
        try:
            actual_log_format = LogFormatType(actual_log_format.lower())
        except ValueError:
            actual_log_format = LogFormatType.DEFAULT

    if actual_log_format is None:
        actual_log_format = get_log_format()

    if not isinstance(actual_log_format, LogFormatType):
        actual_log_format = LogFormatType.DEFAULT

    config = {
        "excluded_instrumentations": excluded_instrumentations or get_excluded_instrumentations(),
        "service_name": service_name or get_config("SERVICE_NAME"),
        "service_version": service_version or get_config("SERVICE_VERSION"),
        "service_instance_id": service_instance_id or get_config("SERVICE_INSTANCE_ID"),
        "otlp_endpoint": otlp_endpoint or get_config("EXPORTER_OTLP_ENDPOINT"),
        "otlp_insecure": otlp_insecure if otlp_insecure is not None else get_boolean_config("EXPORTER_OTLP_INSECURE"),
        "batch_export_delay_ms": batch_export_delay_ms or get_int_config("BATCH_EXPORT_SCHEDULE_DELAY", 120000),
        "enable_resource_detectors": (
            enable_resource_detectors
            if enable_resource_detectors is not None
            else get_boolean_config("RESOURCE_DETECTORS_ENABLED")
        ),
        "enable_logging_instrumentation": (
            enable_logging_instrumentation
            if enable_logging_instrumentation is not None
            else get_boolean_config("LOGGING_INSTRUMENTATION_ENABLED")
        ),
        "propagators": propagators or get_config("OTEL_PROPAGATORS"),
    }

    is_gcp_environment = actual_log_format == LogFormatType.GCP
    default_exporter_type = exporter_type or get_config("EXPORTER_TYPE")

    if not default_exporter_type:
        if is_gcp_environment:
            default_exporter_type = "gcp"
            logger.debug("Auto-detected GCP environment, defaulting to 'gcp' exporter")
        else:
            default_exporter_type = "otlp"

    if default_exporter_type not in ["otlp", "console", "gcp"]:
        logger.warning(f"Invalid exporter type '{default_exporter_type}', defaulting to 'otlp'")
        default_exporter_type = "otlp"

    if default_exporter_type == "gcp" and actual_log_format != LogFormatType.GCP:
        actual_log_format = LogFormatType.GCP

    if config["propagators"] and isinstance(config["propagators"], str):
        configure_specific_propagation(config["propagators"].split(","))

    service_name = str(config["service_name"]) if config["service_name"] else None
    service_version = str(config["service_version"]) if config["service_version"] else None
    service_instance_id = str(config["service_instance_id"]) if config["service_instance_id"] else None
    combined_resource_attributes = {
        ResourceAttributes.SERVICE_NAME: service_name,
        ResourceAttributes.SERVICE_VERSION: service_version,
        ResourceAttributes.SERVICE_INSTANCE_ID: service_instance_id,
    }
    final_resource = detect_resources(combined_resource_attributes)

    initializer = TelemetryInitializer(
        service_name=service_name,
        service_version=service_version,
        resource_attributes=final_resource,
        log_level=actual_log_level,
        log_format=actual_log_format,
        safe_logging=actual_safe_logging,
        otlp_endpoint=str(config["otlp_endpoint"]) if config["otlp_endpoint"] else None,
        otlp_insecure=bool(config["otlp_insecure"]) if config["otlp_insecure"] is not None else None,
        batch_export_delay_ms=int(str(config["batch_export_delay_ms"])) if config["batch_export_delay_ms"] else None,
        enable_resource_detectors=bool(config["enable_resource_detectors"]),
        exporter_type=default_exporter_type,
        traces_exporter_type=traces_exporter_type,
        metrics_exporter_type=metrics_exporter_type,
        logs_exporter_type=logs_exporter_type,
        enable_traces=bool(enable_traces) if enable_traces is not None else True,
        enable_metrics=bool(enable_metrics) if enable_metrics is not None else True,
        enable_logs=bool(enable_logs) if enable_logs is not None else True,
    )

    logger_provider = initializer.configure_logging(resource=final_resource)
    meter_provider = initializer.configure_metrics(resource=final_resource)
    tracer_provider = initializer.configure_tracing(resource=final_resource)

    initializer.setup_exception_handling()

    Resource.create(attributes=final_resource.attributes)
    if logger_provider:
        _logs.set_logger_provider(logger_provider)
    if tracer_provider:
        trace.set_tracer_provider(tracer_provider)
    if meter_provider:
        metrics.set_meter_provider(meter_provider)

    excluded_instr = config["excluded_instrumentations"]
    if not isinstance(excluded_instr, list):
        excluded_instr = [] if excluded_instr is None else [str(excluded_instr)]

    configure_instrumentation(
        tracer_provider=tracer_provider,
        logger_provider=logger_provider,
        meter_provider=meter_provider,
        flask_app=flask_app,
        fastapi_app=fastapi_app,
        celery_app=celery_app,
        log_level=actual_log_level,
        safe_logging=actual_safe_logging,
        excluded_instrumentations=excluded_instr,
        enable_logging_instrumentation=(
            bool(config["enable_logging_instrumentation"])
            if config["enable_logging_instrumentation"] is not None
            else None
        ),
        logs_exporter_type=logs_exporter_type,
        enable_system_metrics=enable_system_metrics,
    )

    logger.info(f"Final resource: {final_resource.attributes}")

    trace_status = "enabled" if tracer_provider else "disabled"
    metrics_status = "enabled" if meter_provider else "disabled"
    logs_status = "enabled" if logger_provider else "disabled"

    log_format_info = ""
    if actual_log_format == LogFormatType.GCP:
        log_format_info = " - GCP log format enabled (logs to stdout)"
        logs_status = "GCP-formatted"

    is_gcp_traces = initializer.exporter_config.get("traces_exporter_type") == "gcp"
    is_gcp_metrics = initializer.exporter_config.get("metrics_exporter_type") == "gcp"
    is_gcp_logs = initializer.exporter_config.get("logs_exporter_type") == "gcp"

    if is_gcp_traces or is_gcp_metrics or is_gcp_logs:
        gcp_services = []
        if is_gcp_traces:
            gcp_services.append("Cloud Trace")
        if is_gcp_metrics:
            gcp_services.append("Cloud Monitoring")
        if is_gcp_logs:
            gcp_services.append("Cloud Logging")

        log_format_info += f" - GCP exporters enabled ({', '.join(gcp_services)})"

    logger.debug(
        f"Telemetry initialized for service: {config['service_name']}{log_format_info} - "
        f"traces: {trace_status}/{initializer.exporter_config.get('traces_exporter_type')}, "
        f"metrics: {metrics_status}/{initializer.exporter_config.get('metrics_exporter_type')}, "
        f"logs: {logs_status}/{initializer.exporter_config.get('logs_exporter_type') if logs_status != 'GCP-formatted' else 'stdout'}"
    )
