"""
Flask-specific instrumentation for DTA Observability.
"""

import logging
from typing import Any, Dict, List, Tuple, Union

from opentelemetry.instrumentation.flask import FlaskInstrumentor as OTelFlaskInstrumentor

from dta_observability.instrumentation.base import BaseHttpInstrumentor
from dta_observability.instrumentation.utils import (
    check_instrumentation_status,
    handle_instrumentation_error,
)
from dta_observability.logging.logger import get_logger


class FlaskInstrumentor(BaseHttpInstrumentor):
    """Handles Flask-specific instrumentation."""

    _INSTRUMENTED_KEY = "_dta_flask_instrumented"

    def __init__(
        self,
        tracer_provider=None,
        logger_provider=None,
        meter_provider=None,
        log_level=logging.INFO,
        logs_exporter_type=None,
    ):
        """
        Initialize the Flask instrumentor.

        Args:
            tracer_provider: Optional tracer provider
            logger_provider: Optional logger provider
            meter_provider: Optional meter provider
            log_level: The logging level to use
            logs_exporter_type: The type of logs exporter being used
        """
        super().__init__(tracer_provider, logger_provider, meter_provider, log_level)
        self.logger = get_logger("dta_observability.instrumentation")
        self.logs_exporter_type = logs_exporter_type
        self.tracer_provider = tracer_provider
        self.logger_provider = logger_provider
        self.meter_provider = meter_provider

    def _get_library_name(self) -> str:
        """Get the library name."""
        return "flask"

    def instrument(self, app: Any) -> bool:
        """
        Instrument a Flask application.

        Args:
            app: The Flask application to instrument

        Returns:
            True if successful, False otherwise
        """
        if not app:
            return False

        try:
            if check_instrumentation_status(app, self._get_library_name(), self._INSTRUMENTED_KEY):
                self.logger.debug("Flask app already instrumented, skipping")
                return True

            self._apply_flask_instrumentation(app)

            if hasattr(app, "config") and app.config.get("ENABLE_FORK_HOOKS", False):
                self._add_gunicorn_fork_hooks(app)

            setattr(app, self._INSTRUMENTED_KEY, True)
            self.register_app(app)
            self.logger.debug("Flask app instrumented with JSON access logging: %s", app)
            return True

        except Exception as e:
            handle_instrumentation_error(self.logger, "Flask", e)
            return False

    def _apply_flask_instrumentation(self, app: Any) -> None:
        """
        Apply OpenTelemetry instrumentation to a Flask app.

        This method uses the OpenTelemetry FlaskInstrumentor for more
        consistent behavior with official instrumentation.

        Args:
            app: The Flask application to instrument
        """
        try:

            from dta_observability.instrumentation.utils import configure_framework_logging

            configure_framework_logging(self.log_level)

            access_logger = get_logger("dta_observability.flask.logs")

            def request_hook(span: Any, environ: Dict[str, Any]) -> None:
                """Hook called on each request."""
                if not span or not span.is_recording():
                    return

                request_data = {
                    "method": environ.get("REQUEST_METHOD", ""),
                    "path": environ.get("PATH_INFO", ""),
                    "query": environ.get("QUERY_STRING", ""),
                    "client_ip": environ.get("REMOTE_ADDR", ""),
                    "user_agent": environ.get("HTTP_USER_AGENT", ""),
                    "referer": environ.get("HTTP_REFERER", ""),
                    "http_version": environ.get("SERVER_PROTOCOL", ""),
                }

                self.server_request_hook(span, request_data)

            def response_hook(span: Any, status: Union[str, int], response_headers: List[Tuple[str, str]]) -> None:
                """
                Hook called after each response.

                Args:
                    span: The current span
                    status: Response status code
                    response_headers: List of response headers
                """
                if not span or not span.is_recording():
                    return

                request_data = {
                    "method": "",
                    "path": "",
                    "query": "",
                    "client_ip": "unknown",
                    "user_agent": "",
                    "referer": "",
                    "http_version": "",
                }

                if hasattr(span, "attributes") and span.attributes:

                    attr_mapping = {
                        "http.method": "method",
                        "http.target": "path",
                        "http.user_agent": "user_agent",
                        "http.referer": "referer",
                        "http.flavor": "http_version",
                        "http.client_ip": "client_ip",
                    }

                    for otel_key, our_key in attr_mapping.items():
                        if otel_key in span.attributes:
                            request_data[our_key] = span.attributes[otel_key]

                    if "http.target" in span.attributes:
                        target = span.attributes["http.target"]
                        if "?" in target:
                            request_data["query"] = target.split("?", 1)[1]

                    if "http.route" in span.attributes:
                        request_data["path"] = span.attributes["http.route"]
                    elif "http.target" in span.attributes:
                        target = span.attributes["http.target"]
                        request_data["path"] = target.split("?")[0] if "?" in target else target

                status_code = int(status.split(" ")[0]) if isinstance(status, str) else status

                if access_logger:
                    self.process_response(span, request_data, status_code, access_logger, set())

            OTelFlaskInstrumentor().instrument_app(
                app,
                request_hook=request_hook,
                response_hook=response_hook,
                tracer_provider=self.tracer_provider,
                meter_provider=self.meter_provider,
            )

            if not hasattr(app, "dta_config"):
                app.dta_config = {}
            app.dta_config["logging_configured"] = True

            self.logger.info("Flask app instrumented with OpenTelemetry instrumentation")

        except ImportError:
            self.logger.warning(
                "OpenTelemetry Flask instrumentation not available. "
                "Install with: pip install opentelemetry-instrumentation-flask"
            )
            raise
        except Exception as e:
            self.logger.error(f"Failed to instrument Flask app: {e}", exc_info=True)
            raise

    def _add_gunicorn_fork_hooks(self, app: Any) -> None:
        """
        Add post-fork hooks for Gunicorn workers.

        This helps handle the issue where BatchSpanProcessor is not fork-safe.

        Args:
            app: The Flask application
        """
        if hasattr(app, "dta_observability_post_fork"):
            return

        def post_fork(server, worker):
            """
            Re-initialize telemetry in forked worker processes.

            This fixes the issue with BatchSpanProcessor not being fork-safe.
            """
            from dta_observability.logging.logger import get_logger

            worker_logger = get_logger("dta_observability.worker")
            exporter_type = app.config.get("EXPORTER_TYPE", "otlp")

            worker_logger.debug(f"Telemetry reinitialized in worker process with {exporter_type} exporter")

        app.dta_observability_post_fork = post_fork
        self.logger.debug("Gunicorn post_fork hooks registered for fork-safe BatchSpanProcessor")
