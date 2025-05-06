"""
Instrumentation utilities for DTA Observability.
"""

import logging
from typing import Any, Optional


def handle_instrumentation_error(
    logger: logging.Logger, library_name: str, error: Exception, context: str = "instrumentation"
) -> None:
    """
    Handle instrumentation errors consistently.

    Args:
        logger: Logger to use for recording errors
        library_name: The name of the library that failed to instrument
        error: The exception that was raised
        context: Context where the error occurred (default: "instrumentation")
    """
    logger.warning("Failed to instrument %s (%s): %s - %s", library_name, context, error.__class__.__name__, str(error))
    logger.debug("Instrumentation error details", exc_info=error)


def configure_framework_logging(log_level: Optional[int] = None) -> None:
    """
    Configure logging for web servers like gunicorn and werkzeug.

    Args:
        log_level: Logging level to apply
    """

    if log_level == logging.DEBUG:
        log_level = logging.DEBUG
    else:
        log_level = logging.ERROR

    all_loggers = [
        logging.getLogger("werkzeug"),
        logging.getLogger("werkzeug.access"),
        logging.getLogger("werkzeug.error"),
        logging.getLogger("uvicorn"),
        logging.getLogger("uvicorn.access"),
        logging.getLogger("uvicorn.error"),
        logging.getLogger("fastapi"),
        logging.getLogger("fastapi.access"),
        logging.getLogger("fastapi.error"),
        logging.getLogger("fastapi.routing"),
        logging.getLogger("gunicorn"),
        logging.getLogger("gunicorn.error"),
        logging.getLogger("gunicorn.access"),
        logging.getLogger("celery"),
        logging.getLogger("celery.app"),
        logging.getLogger("celery.app.trace"),
        logging.getLogger("flask"),
        logging.getLogger("flask.app"),
        logging.getLogger("flask.error"),
        logging.getLogger("flask.access"),
    ]

    for logger in all_loggers:
        logger.setLevel(log_level)
        logger.propagate = True


def check_instrumentation_status(object_to_check: Any, library_name: str, attr_name: str) -> bool:
    """
    Check if an object has already been instrumented.

    Args:
        object_to_check: The object to check for instrumentation status
        library_name: The name of the library being instrumented (for logging)
        attr_name: The attribute name that marks the object as instrumented

    Returns:
        True if the object is already instrumented, False otherwise
    """
    return hasattr(object_to_check, attr_name) and bool(getattr(object_to_check, attr_name))


def httpx_request_hook(span, request):
    """Modify the span name for httpx requests."""
    method = request.method.decode() if isinstance(request.method, bytes) else request.method
    url = str(request.url)
    span.update_name(f"{method} {url}")


async def httpx_async_request_hook(span, request):
    """Modify the span name for httpx requests."""
    method = request.method.decode() if isinstance(request.method, bytes) else request.method
    url = str(request.url)
    span.update_name(f"{method} {url}")


def fastapi_server_request_hook(span, request):
    method = request.get("method")
    path = request.get("path")
    span.update_name(f"{method} {path}")


def fastapi_client_request_hook(span, request, message):
    method = request.get("method")
    path = request.get("path")
    span.update_name(f"{method} {path} http receive")


def fastapi_client_response_hook(span, request, message):
    method = request.get("method")
    path = request.get("path")
    if message.get("type") == "http.response.start":
        span.update_name(f"{method} {path} http response start")
    else:
        span.update_name(f"{method} {path} http response end")
