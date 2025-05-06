"""
FastAPI-specific instrumentation for DTA Observability.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, Optional, Set

from fastapi import Request
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor as OTelFastAPIInstrumentor
from starlette.middleware.base import BaseHTTPMiddleware

from dta_observability.core.config import get_log_format
from dta_observability.instrumentation.base import BaseHttpInstrumentor, TraceContextMiddleware
from dta_observability.instrumentation.utils import (
    check_instrumentation_status,
    configure_framework_logging,
    handle_instrumentation_error,
)
from dta_observability.logging.logger import get_logger


class AccessLogMiddleware(BaseHTTPMiddleware):
    """Middleware to handle access logging in FastAPI with JSON format."""

    def __init__(self, app, log_format=None):
        super().__init__(app)
        self.logger = get_logger("dta_observability.fastapi.access")
        self.log_format = log_format

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        forwarded_for = request.headers.get("x-forwarded-for", "")
        client_ip = (
            forwarded_for.split(",")[0].strip()
            if forwarded_for
            else (request.client.host if request.client else "unknown")
        )

        try:
            response = await call_next(request)

            duration = time.time() - start_time

            self.logger.info(
                f"{request.method} {request.url.path} {response.status_code}",
                extra={
                    "http_client_ip": client_ip,
                    "http_method": request.method,
                    "http_path": request.url.path,
                    "http_status_code": response.status_code,
                    "http_request_time": f"{duration:.4f}s",
                    "http_user_agent": request.headers.get("user-agent", ""),
                    "http_referer": request.headers.get("referer", ""),
                },
            )

            return response
        except Exception as exc:
            duration = time.time() - start_time
            self.logger.error(
                f"Error processing request: {exc}",
                extra={
                    "http_client_ip": client_ip,
                    "http_method": request.method,
                    "http_path": request.url.path,
                    "http_request_time": f"{duration:.4f}s",
                    "error": str(exc),
                    "error_type": exc.__class__.__name__,
                },
            )
            raise


class FastAPIInstrumentor(BaseHttpInstrumentor):
    """Handles FastAPI-specific instrumentation."""

    _INSTRUMENTED_KEY = "_dta_fastapi_instrumented"

    def __init__(
        self,
        tracer_provider=None,
        logger_provider=None,
        meter_provider=None,
        log_level=None,
        logs_exporter_type=None,
    ):
        """
        Initialize the FastAPI instrumentor.

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

    def _get_library_name(self) -> str:
        """Get the library name."""
        return "fastapi"

    def _setup_exception_handlers(self, app: Any) -> None:
        """
        Set up exception handlers for FastAPI application.

        Args:
            app: The FastAPI application instance
        """
        from fastapi import Request
        from fastapi.responses import JSONResponse

        from dta_observability.core.span import mark_error_event
        from dta_observability.logging.logger import DTAErrorHandler

        @app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:

            trace_id = getattr(request.state, "trace_id", None)
            span_id = getattr(request.state, "span_id", None)

            mark_error_event(exc, handled=False)

            error_handler = DTAErrorHandler()

            error_handler.handle(exc)

            error_response = {
                "error": str(exc),
                "type": exc.__class__.__name__,
            }

            if trace_id:
                error_response.update(
                    {
                        "trace_id": str(trace_id) if trace_id else "",
                        "span_id": str(span_id) if span_id else "",
                    }
                )

            return JSONResponse(
                status_code=500,
                content=error_response,
            )

        loop = asyncio.get_event_loop()
        default_handler = loop.get_exception_handler()

        def exception_handler(loop: asyncio.AbstractEventLoop, context: dict) -> None:
            exc = context.get("exception")
            if exc:
                error_handler = DTAErrorHandler()
                error_handler.handle(exc)

            if default_handler is not None:
                default_handler(loop, context)

        loop.set_exception_handler(exception_handler)

    def instrument_app(self, app: Any) -> bool:
        """
        Instrument a FastAPI application.

        Args:
            app: The FastAPI application to instrument

        Returns:
            True if successful, False otherwise
        """
        if not app:
            return False

        try:
            if check_instrumentation_status(app, self._get_library_name(), self._INSTRUMENTED_KEY):
                self.logger.debug("FastAPI app already instrumented, skipping")
                return True

            self._instrument_app(app)

            setattr(app, self._INSTRUMENTED_KEY, True)
            self.register_app(app)
            self.logger.debug("FastAPI app instrumented: %s", app)

            self._setup_exception_handlers(app)

            return True

        except Exception as e:
            handle_instrumentation_error(self.logger, "FastAPI", e)
            return False

    def _setup_lifespan(self, app: Any) -> None:
        """
        Set up lifespan context manager for FastAPI application.
        This helps prevent duplicate logging from uvicorn.

        Args:
            app: The FastAPI application instance
        """

        @asynccontextmanager
        async def lifespan(app_instance: Any) -> AsyncIterator:

            logging.getLogger("uvicorn.access").handlers = []
            logging.getLogger("uvicorn.access").propagate = False
            logging.getLogger("access").propagate = False

            yield

        app.router.lifespan_context = lifespan

    def _instrument_app(self, app: Any) -> None:
        """
        Apply OpenTelemetry instrumentation to a FastAPI app.

        This method uses the OpenTelemetry FastAPIInstrumentor for more
        consistent behavior with official instrumentation.

        Args:
            app: The FastAPI application to instrument
        """
        try:
            self._setup_lifespan(app)
            configure_framework_logging(log_level=self.log_level)

            app.add_middleware(TraceContextMiddleware)

            log_format = get_log_format()
            app.add_middleware(AccessLogMiddleware, log_format=log_format)
            access_logger = get_logger("dta_observability.fastapi.logs")
            logged_spans: Set[str] = set()

            def server_request_hook(span: Any, scope: Dict[str, Any]) -> None:
                if not span or not span.is_recording():
                    return

                scope["span_context"] = span

                headers = scope.get("headers", [])
                headers_dict = {}
                for k, v in headers:
                    if k and v:
                        try:
                            key = k.decode("utf-8") if isinstance(k, bytes) else k
                            value = v.decode("utf-8") if isinstance(v, bytes) else v
                            headers_dict[key.lower()] = value
                        except (UnicodeDecodeError, AttributeError):
                            continue

                client_ip = scope.get("client", ("unknown", 0))[0]
                forwarded_for = headers_dict.get("x-forwarded-for", "")
                if forwarded_for:
                    client_ip = forwarded_for.split(",")[0].strip()

                request_data = {
                    "method": scope.get("method", ""),
                    "path": scope.get("path", ""),
                    "route": scope.get("route", ""),
                    "query": scope.get("query_string", b"").decode("utf-8"),
                    "client_ip": client_ip,
                    "user_agent": headers_dict.get("user-agent", ""),
                    "referer": headers_dict.get("referer", ""),
                    "http_version": scope.get("http_version", ""),
                }

                from dta_observability.instrumentation.utils import fastapi_server_request_hook

                fastapi_server_request_hook(span, request_data)

                self.server_request_hook(span, request_data)

            def client_response_hook(span: Any, scope: Dict[str, Any], message: Dict[str, Any]) -> None:
                if not span or not span.is_recording():
                    return

                if message.get("type") != "http.response.start":
                    return

                status_code = message.get("status", 0)
                if status_code == 0:
                    return

                headers = scope.get("headers", [])
                headers_dict = {}
                for k, v in headers:
                    if k and v:
                        try:
                            key = k.decode("utf-8") if isinstance(k, bytes) else k
                            value = v.decode("utf-8") if isinstance(v, bytes) else v
                            headers_dict[key.lower()] = value
                        except (UnicodeDecodeError, AttributeError):
                            continue

                client_ip = scope.get("client", ("unknown", 0))[0]
                forwarded_for = headers_dict.get("x-forwarded-for", "")
                if forwarded_for:
                    client_ip = forwarded_for.split(",")[0].strip()

                request_data = {
                    "method": scope.get("method", ""),
                    "path": scope.get("path", ""),
                    "route": scope.get("route", ""),
                    "query": scope.get("query_string", b"").decode("utf-8"),
                    "client_ip": client_ip,
                    "user_agent": headers_dict.get("user-agent", ""),
                    "referer": headers_dict.get("referer", ""),
                    "http_version": scope.get("http_version", ""),
                }

                from dta_observability.instrumentation.utils import fastapi_client_response_hook

                fastapi_client_response_hook(span, request_data, message)

                if access_logger:
                    self.process_response(span, request_data, status_code, access_logger, logged_spans)

            OTelFastAPIInstrumentor.instrument_app(
                app,
                server_request_hook=server_request_hook,
                client_response_hook=client_response_hook,
                tracer_provider=self.tracer_provider,
                meter_provider=self.meter_provider,
                exclude_spans=["send"],
                excluded_urls="client/.*/info,healthcheck",
            )

            if not hasattr(app, "dta_config"):
                app.dta_config = {}
            app.dta_config["logging_configured"] = True

            self.logger.info("FastAPI app instrumented with OpenTelemetry instrumentation")

        except ImportError:
            self.logger.warning(
                "OpenTelemetry ASGI instrumentation not available. "
                "Install with: pip install opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-asgi"
            )
            raise
        except Exception as e:
            self.logger.error(f"Failed to instrument FastAPI app: {e}", exc_info=True)
            raise

    def instrument(self, app: Optional[Any] = None) -> bool:
        """
        Instrument FastAPI application.

        Args:
            app: The FastAPI application instance to instrument

        Returns:
            True if successful, False otherwise
        """
        if not app:
            self.logger.warning("No FastAPI app provided for instrumentation")
            return False

        return self.instrument_app(app)
