"""
Functions for creating instrumentors with hooks.
"""

from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from dta_observability.instrumentation.utils import (
    httpx_async_request_hook,
    httpx_request_hook,
)


def create_requests_instrumentor() -> RequestsInstrumentor:
    """Create a requests instrumentor with the custom request hook.

    Returns:
        A configured RequestsInstrumentor instance
    """
    instrumentor = RequestsInstrumentor()
    instrumentor.instrument(request_hook=httpx_request_hook)
    return instrumentor


def create_httpx_instrumentor() -> HTTPXClientInstrumentor:
    """Create an HTTPX instrumentor with the custom request hooks.

    Returns:
        A configured HTTPXClientInstrumentor instance
    """
    instrumentor = HTTPXClientInstrumentor()
    instrumentor.instrument(
        request_hook=httpx_request_hook,
        async_request_hook=httpx_async_request_hook,
    )
    return instrumentor


def instrument_fastapi_client_hooks(span, scope):
    """Add client hooks for FastAPI.

    Args:
        span: The span to modify
        scope: The ASGI scope
    """
    from dta_observability.instrumentation.utils import fastapi_client_request_hook

    request_data = {
        "method": scope.get("method", ""),
        "path": scope.get("path", ""),
    }

    fastapi_client_request_hook(span, request_data, {"type": "http.receive"})
    return request_data
