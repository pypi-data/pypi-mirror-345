"""
Span helpers for manual instrumentation.
"""

import asyncio
import functools
import inspect
import json
from typing import Any, Callable, Dict, Optional, Sequence, TypeVar, Union, cast

from opentelemetry import trace
from opentelemetry.trace import Span, Status, StatusCode

F = TypeVar("F", bound=Callable[..., Any])
T = TypeVar("T")


class SpanAttributeValue:
    """Constants for commonly used span attribute values."""

    CLIENT = "client"
    SERVER = "server"
    INTERNAL = "internal"
    PRODUCER = "producer"
    CONSUMER = "consumer"


class SpanAttribute:
    """Constants for commonly used span attribute keys."""

    FUNCTION_NAME = "function.name"
    FUNCTION_MODULE = "function.module"
    ERROR_TYPE = "error.type"
    ERROR_MESSAGE = "error.message"
    COMPONENT = "component"
    SERVICE_VERSION = "service.version"
    HTTP_METHOD = "http.method"
    HTTP_URL = "http.url"
    HTTP_STATUS_CODE = "http.status_code"
    DB_SYSTEM = "db.system"
    DB_OPERATION = "db.operation"
    DB_STATEMENT = "db.statement"
    MESSAGE_SYSTEM = "messaging.system"
    MESSAGE_OPERATION = "messaging.operation"


def set_span_attribute_safely(span: Span, key: str, value: Any) -> None:
    """
    Set a span attribute with safe type handling.

    Args:
        span: The span to set the attribute on
        key: The attribute key
        value: The attribute value

    This helper ensures the attribute value is of a proper type
    to avoid the "Invalid type for attribute" warnings.
    """
    if value is None:
        return

    processed_value: Union[str, bool, int, float, Sequence[str], Sequence[bool], Sequence[int], Sequence[float]] = str(
        value
    )

    if isinstance(value, dict):
        try:
            processed_value = json.dumps(value)
        except (TypeError, ValueError):
            processed_value = str(value)
    elif isinstance(value, list):
        if all(isinstance(item, str) for item in value):
            processed_value = value
        elif all(isinstance(item, bool) for item in value):
            processed_value = value
        elif all(isinstance(item, int) for item in value):
            processed_value = value
        elif all(isinstance(item, float) for item in value):
            processed_value = value
        else:
            processed_value = str(value)
    elif isinstance(value, (str, int, float, bool)):
        processed_value = value

    try:
        span.set_attribute(key, processed_value)
    except Exception:
        try:
            span.set_attribute(key, str(processed_value))
        except Exception:
            pass


def _process_attributes(attributes: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process attributes to ensure safe values.

    Args:
        attributes: Raw attributes dictionary

    Returns:
        Dictionary with processed attribute values
    """
    safe_attributes: Dict[str, Any] = {}
    for key, value in attributes.items():
        if value is None:
            continue
        elif isinstance(value, dict):
            try:
                safe_attributes[key] = json.dumps(value)
            except (TypeError, ValueError):
                safe_attributes[key] = str(value)
        elif isinstance(value, list):
            if all(isinstance(item, str) for item in value):
                safe_attributes[key] = value
            elif all(isinstance(item, bool) for item in value):
                safe_attributes[key] = value
            elif all(isinstance(item, int) for item in value):
                safe_attributes[key] = value
            elif all(isinstance(item, float) for item in value):
                safe_attributes[key] = value
            else:
                safe_attributes[key] = str(value)
        elif not isinstance(value, (str, int, float, bool)):
            safe_attributes[key] = str(value)
        else:
            safe_attributes[key] = value
    return safe_attributes


def _handle_exception(
    span: Span, exception: Union[Exception, BaseException], kind: str = "unhandled_exception"
) -> None:
    """
    Handle an exception in a span.

    Args:
        span: The span to set error attributes on
        exception: The exception to record
        kind: The kind of exception ("handled_exception" or "unhandled_exception")
    """
    span.record_exception(exception)
    span.set_status(Status(StatusCode.ERROR, str(exception)))

    set_span_attribute_safely(span, SpanAttribute.ERROR_TYPE, exception.__class__.__name__)
    set_span_attribute_safely(span, SpanAttribute.ERROR_MESSAGE, str(exception))

    span.add_event(
        name="exception",
        attributes={
            "exception.type": exception.__class__.__name__,
            "exception.message": str(exception),
            "error.kind": kind,
        },
    )


def traced(
    name: Optional[Union[str, Callable]] = None,
    attributes: Optional[Dict[str, Any]] = None,
    kind: Optional[trace.SpanKind] = None,
    track_handled_exceptions: bool = True,
) -> Callable[[F], F]:
    """
    Decorator to trace a function.

    Args:
        name: The name of the span. Defaults to the function name.
        attributes: Attributes to add to the span.
        kind: The kind of span (CLIENT, SERVER, INTERNAL, etc.)
        track_handled_exceptions: If True, exceptions will be recorded in spans even if
                               they're handled within the function.

    Returns:
        Decorated function.
    """
    if callable(name):
        func, name = name, None
        return traced()(func)

    def decorator(func: F) -> F:
        span_name = name or func.__name__
        is_coroutine = asyncio.iscoroutinefunction(func)

        if is_coroutine:

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:

                tracer = trace.get_tracer(func.__module__)

                span_attributes = {
                    SpanAttribute.FUNCTION_NAME: func.__name__,
                    SpanAttribute.FUNCTION_MODULE: func.__module__,
                }

                if attributes:
                    span_attributes.update(attributes)

                safe_attributes = _process_attributes(span_attributes)

                actual_kind = kind if kind is not None else trace.SpanKind.INTERNAL

                with tracer.start_as_current_span(span_name, attributes=safe_attributes, kind=actual_kind) as span:
                    has_recorded_exception = False

                    try:
                        result = await func(*args, **kwargs)
                        if not has_recorded_exception:
                            span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        _handle_exception(span, e)
                        has_recorded_exception = True
                        raise
                    finally:
                        if track_handled_exceptions and not has_recorded_exception:
                            import sys

                            exc_info = sys.exc_info()
                            if exc_info[0] is not None and exc_info[1] is not None:
                                _handle_exception(
                                    span,
                                    exc_info[1] if isinstance(exc_info[1], Exception) else Exception(str(exc_info[1])),
                                    "handled_exception",
                                )

            return cast(F, async_wrapper)
        else:

            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:

                tracer = trace.get_tracer(func.__module__)

                span_attributes = {
                    SpanAttribute.FUNCTION_NAME: func.__name__,
                    SpanAttribute.FUNCTION_MODULE: func.__module__,
                }

                if attributes:
                    span_attributes.update(attributes)

                safe_attributes = _process_attributes(span_attributes)

                actual_kind = kind if kind is not None else trace.SpanKind.INTERNAL

                with tracer.start_as_current_span(span_name, attributes=safe_attributes, kind=actual_kind) as span:
                    has_recorded_exception = False

                    try:
                        result = func(*args, **kwargs)
                        if not has_recorded_exception:
                            span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        _handle_exception(span, e)
                        has_recorded_exception = True
                        raise
                    finally:
                        if track_handled_exceptions and not has_recorded_exception:
                            import sys

                            exc_info = sys.exc_info()
                            if exc_info[0] is not None and exc_info[1] is not None:
                                _handle_exception(
                                    span,
                                    exc_info[1] if isinstance(exc_info[1], Exception) else Exception(str(exc_info[1])),
                                    "handled_exception",
                                )

            return cast(F, sync_wrapper)

    return decorator


class TracerFactory:
    """
    Factory to create tracers with proper naming and configuration.
    """

    @staticmethod
    def create(name: Optional[str] = None) -> "Tracer":
        """
        Create a new tracer instance.

        Args:
            name: Optional name for the tracer. If not provided, uses caller's module.

        Returns:
            A configured Tracer instance
        """
        return Tracer(name)


class Tracer:
    """
    Simple wrapper around OpenTelemetry tracer to create spans.
    """

    def __init__(self, name: Optional[str] = None) -> None:
        """
        Initialize the tracer.

        Args:
            name: The name of the tracer. Defaults to the caller's module name.
        """
        if name is None:
            frame = inspect.currentframe()
            try:
                if frame and frame.f_back:
                    name = frame.f_back.f_globals.get("__name__", "unknown")
            except (AttributeError, ValueError):
                name = "unknown"
            finally:
                del frame

        self._tracer = trace.get_tracer(name or "unknown")

    def start_span(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        kind: Optional[trace.SpanKind] = None,
    ) -> Span:
        """
        Start a new span.

        Args:
            name: The name of the span.
            attributes: Attributes to add to the span.
            kind: The kind of span.

        Returns:
            The created span.
        """
        actual_kind = kind if kind is not None else trace.SpanKind.INTERNAL
        safe_attributes = _process_attributes(attributes or {})
        return self._tracer.start_span(name, attributes=safe_attributes, kind=actual_kind)

    def start_as_current_span(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        kind: Optional[trace.SpanKind] = None,
    ) -> Any:
        """
        Start a new span as the current active span.

        Args:
            name: The name of the span.
            attributes: Attributes to add to the span.
            kind: The kind of span.

        Returns:
            The created span.
        """
        actual_kind = kind if kind is not None else trace.SpanKind.INTERNAL
        safe_attributes = _process_attributes(attributes or {})
        return self._tracer.start_as_current_span(name, attributes=safe_attributes, kind=actual_kind)


def get_current_span() -> Span:
    """
    Get the current active span.

    Returns:
        The current active span.
    """
    return trace.get_current_span()


def mark_error_event(exception: Exception, handled: bool = True) -> None:
    """
    Mark the current span with an error event for the given exception.

    This helper makes it easy to manually record exceptions in spans, particularly
    when using try/except blocks where exceptions are handled.

    Args:
        exception: The exception to record
        handled: Whether this is a handled exception (default True)

    Example:
        ```python
        from dta_observability import mark_error_event

        try:
            # Some risky operation
            result = 1 / 0
        except Exception as e:
            # Handle the exception but record it in the current span
            mark_error_event(e)
            # Continue with fallback behavior
        ```
    """
    current_span = get_current_span()

    if current_span and current_span.is_recording():
        _handle_exception(current_span, exception, "handled_exception" if handled else "unhandled_exception")


def add_span_attribute(key: str, value: Any) -> None:
    """
    Add an attribute to the current active span.

    Args:
        key: The attribute key
        value: The attribute value
    """
    span = get_current_span()

    if span and span.is_recording():
        set_span_attribute_safely(span, key, value)


def add_span_attributes(attributes: Dict[str, Any]) -> None:
    """
    Add multiple attributes to the current active span.

    Args:
        attributes: Dictionary of attribute keys and values
    """
    span = get_current_span()

    if span and span.is_recording():
        safe_attributes = _process_attributes(attributes)
        for key, value in safe_attributes.items():
            span.set_attribute(key, value)


def set_span_status(code: StatusCode, description: Optional[str] = None) -> None:
    """
    Set the status of the current active span.

    Args:
        code: The status code (OK or ERROR)
        description: Optional description
    """
    span = get_current_span()

    if span and span.is_recording():
        span.set_status(Status(code, description))


def create_span(name: str, kind: Optional[trace.SpanKind] = None, attributes: Optional[Dict[str, Any]] = None) -> Any:
    """
    Create a new span and use it as the current span.

    This is a convenience function to create a span for use in a context manager,
    ensuring proper trace context propagation for logs within the span.

    Args:
        name: Name of the span
        kind: The kind of span (SERVER, CLIENT, INTERNAL, etc.)
        attributes: Attributes to add to the span

    Returns:
        A span context manager that can be used in a 'with' statement

    Example:
        ```python
        from dta_observability import create_span, get_logger

        # Create a logger
        logger = get_logger("my_module")

        # Create a span to ensure log correlation
        with create_span("my_operation"):
            logger.debug("This log will have trace context")
        ```
    """

    tracer = trace.get_tracer("dta_observability")

    actual_kind = kind if kind is not None else trace.SpanKind.INTERNAL
    safe_attributes = _process_attributes(attributes or {})
    return tracer.start_as_current_span(name, kind=actual_kind, attributes=safe_attributes)
