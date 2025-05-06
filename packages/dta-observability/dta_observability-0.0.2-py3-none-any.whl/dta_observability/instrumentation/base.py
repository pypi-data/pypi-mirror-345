"""
Base classes for instrumentation.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

from opentelemetry import trace
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace import Span, TracerProvider
from opentelemetry.trace import SpanKind
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from dta_observability.core.span import set_span_attribute_safely
from dta_observability.instrumentation.registry import instrumentation_registry
from dta_observability.logging.logger import DTAErrorHandler, get_logger


class BaseInstrumentor(ABC):
    """
    Base class for all instrumentors.

    Provides common functionality and enforces a consistent interface.
    """

    def __init__(
        self,
        tracer_provider: Optional[TracerProvider] = None,
        logger_provider: Optional[LoggerProvider] = None,
        meter_provider: Optional[MeterProvider] = None,
        log_level: Optional[int] = None,
    ):
        """
        Initialize the instrumentor.

        Args:
            tracer_provider: Optional tracer provider to use
            logger_provider: Optional logger provider to use
            meter_provider: Optional meter provider to use
            log_level: Optional log level to use for this instrumentor
        """
        self.tracer_provider = tracer_provider
        self.logger_provider = logger_provider
        self.log_level = log_level
        self.meter_provider = meter_provider
        self.logger = get_logger(f"dta_observability.instrumentation.{self._get_library_name()}")

    @abstractmethod
    def _get_library_name(self) -> str:
        """
        Get the name of the library being instrumented.

        Returns:
            The library name as a string
        """
        pass

    @abstractmethod
    def instrument(self, app: Any) -> bool:
        """
        Instrument a specific application instance.

        Args:
            app: The application instance to instrument

        Returns:
            True if successful, False otherwise
        """
        pass

    def is_globally_instrumented(self) -> bool:
        """
        Check if the library is already globally instrumented.

        Returns:
            True if globally instrumented, False otherwise
        """
        return instrumentation_registry.is_globally_instrumented(self._get_library_name())

    def set_globally_instrumented(self) -> None:
        """Mark the library as globally instrumented."""
        instrumentation_registry.set_globally_instrumented(self._get_library_name())

    def is_app_instrumented(self, app: Any) -> bool:
        """
        Check if a specific app is already instrumented.

        Args:
            app: The application instance to check

        Returns:
            True if already instrumented, False otherwise
        """
        return instrumentation_registry.is_app_instrumented(self._get_library_name(), app)

    def register_app(self, app: Any) -> None:
        """
        Register an app as instrumented.

        Args:
            app: The application instance to register
        """
        instrumentation_registry.register_app(self._get_library_name(), app)


class TraceContextMiddleware(BaseHTTPMiddleware):
    """Middleware to ensure trace context is preserved."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:

        current_span = trace.get_current_span()
        if current_span:
            span_context = current_span.get_span_context()
            if span_context:

                request.state.trace_id = format(span_context.trace_id, "032x")
                request.state.span_id = format(span_context.span_id, "016x")
                request.state.trace_sampled = span_context.trace_flags.sampled

        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            error_handler = DTAErrorHandler()
            error_handler.handle(exc)

            error_response = {
                "error": str(exc),
                "type": exc.__class__.__name__,
            }

            if hasattr(request.state, "trace_id"):
                error_response.update(
                    {
                        "trace_id": request.state.trace_id,
                        "span_id": request.state.span_id,
                    }
                )

            return JSONResponse(
                status_code=500,
                content=error_response,
            )


class BaseHttpInstrumentor(BaseInstrumentor):
    """
    Base class for HTTP framework instrumentors (Flask, FastAPI, etc.).

    Provides common HTTP instrumentation functionality.
    """

    def server_request_hook(self, span: Span, request_data: Dict[str, Any]) -> None:
        """
        Process server request for span enrichment.

        Args:
            span: The current span
            request_data: Dictionary with request data (method, path, etc.)
        """
        if not span or not span.is_recording():
            return

        span._kind = SpanKind.SERVER

        method = request_data.get("method", "")
        path = request_data.get("path", "")
        route = request_data.get("route", "")

        if route and hasattr(route, "path") and route.path:
            path = route.path

        if method and path:
            set_span_attribute_safely(span, "http.route", path)
            set_span_attribute_safely(span, "http.method", method)

        if hasattr(span, "set_attribute"):
            import time

            span.set_attribute("http.request_start_time", time.time())

    def process_response(
        self,
        span: Span,
        request_data: Dict[str, Any],
        status_code: Union[int, str],
        access_logger: Any,
        logged_spans: Any,
    ) -> None:
        """
        Process HTTP response for span enrichment and access logging.

        Args:
            span: The current span
            request_data: Dictionary with request data
            status_code: HTTP status code
            access_logger: Logger for access logs
            logged_spans: Set of already logged span IDs
        """
        if not span or not span.is_recording():
            return

        import logging
        import time

        span_id = getattr(span, "span_id", None)
        if span_id in logged_spans:
            return

        try:

            if isinstance(status_code, str):
                status_code = int(status_code.split()[0]) if status_code else 0

            if status_code >= 500:
                from opentelemetry.trace import Status, StatusCode

                span.set_status(Status(StatusCode.ERROR, f"HTTP {status_code} Server Error"))
            elif status_code >= 400:
                from opentelemetry.trace import Status, StatusCode

                span.set_status(Status(StatusCode.ERROR, f"HTTP {status_code} Client Error"))
            else:

                from opentelemetry.trace import Status, StatusCode

                span.set_status(Status(StatusCode.OK))

            set_span_attribute_safely(span, "http.status_code", status_code)

            request_time = "unknown"
            if (
                hasattr(span, "attributes")
                and span.attributes is not None
                and "http.request_start_time" in span.attributes
            ):
                start_time = span.attributes.get("http.request_start_time")
                if start_time and isinstance(start_time, (int, float)):
                    request_time = f"{time.time() - start_time:.4f}s"

            if span_id:
                logged_spans.add(span_id)

            log_level = logging.INFO
            if status_code >= 500:
                log_level = logging.ERROR
            elif status_code >= 400:
                log_level = logging.WARNING

            method = request_data.get("method", "")
            path = request_data.get("path", "")
            client_ip = request_data.get("client_ip", "unknown")
            user_agent = request_data.get("user_agent", "")
            referer = request_data.get("referer", "")
            query = request_data.get("query", "")
            http_version = request_data.get("http_version", "")

            access_logger.log(
                log_level,
                f"{method} {path} {status_code}",
                extra={
                    "http_client_ip": client_ip,
                    "http_method": method,
                    "http_path": path,
                    "http_query": query,
                    "http_version": http_version,
                    "http_status_code": status_code,
                    "http_request_time": request_time,
                    "http_user_agent": user_agent,
                    "http_referer": referer,
                },
            )
        except Exception as e:
            logging.getLogger("dta_observability").error(f"Error in HTTP access log hook: {e}", exc_info=True)
