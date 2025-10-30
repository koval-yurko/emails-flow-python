import os
from functools import wraps
from opentelemetry import trace

_tracer = None

def _init_tracer():
    global _tracer
    if _tracer is None:
        _tracer = trace.get_tracer(__name__)
    return _tracer

def _parse_headers(headers_str):
    """Parse headers string into dict format for gRPC metadata"""
    if not headers_str:
        return None

    # Handle comma-separated key=value pairs
    headers_dict = {}
    for header in headers_str.split(","):
        if "=" in header:
            key, value = header.split("=", 1)
            # gRPC metadata keys must be lowercase
            headers_dict[key.strip().lower()] = value.strip()

    return headers_dict if headers_dict else None

def trace_operation(namespace=None, operation_name=None, **default_attributes):
    """
    Decorator to add OpenTelemetry tracing to 3-rd party calls.

    Usage:
        @trace_operation("get_email")
        def get_email_by_id(self, row_id):
            ...

    Args:
        namespace: Namespace prefix for the span name
        operation_name: Name of the operation (defaults to function name)
        **default_attributes: Additional attributes to add to the span
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Initialize tracer if not already done
            tracer = _init_tracer()

            # Use operation name or default to function name
            prefix = f"{namespace}." if namespace else ""
            span_name = operation_name or f"{prefix}{func.__name__}"

            with tracer.start_as_current_span(span_name) as span:
                # Set any additional default attributes
                for key, value in default_attributes.items():
                    if value is not None:
                        span.set_attribute(key, value)

                # Execute the function
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    # Record exception in span
                    span.set_attribute("error", True)
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    raise

        return wrapper
    return decorator


def lambda_handler_with_trace(func):
    """
    Decorator for Lambda handlers that adds root span tracing.

    For local development: Creates a root span with tracing
    For AWS Lambda: Just runs the handler (OTEL layer handles tracing)

    Usage:
        @lambda_handler_with_trace
        def handler(event, context):
            # your handler code
            pass
    """
    @wraps(func)
    def wrapper(event, context):
        # For local development, create a root span
        if os.getenv("ENVIRONMENT") == 'local':
            tracer = _init_tracer()

            with tracer.start_as_current_span("lambda_handler") as span:
                span.set_attribute("function.name", context.function_name)
                span.set_attribute("faas.trigger", "manual")
                return func(event, context)
        else:
            # In AWS Lambda, just run the handler - OTEL layer creates root span
            return func(event, context)

    return wrapper
