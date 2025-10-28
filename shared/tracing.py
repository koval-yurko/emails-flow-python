from functools import wraps
from opentelemetry import trace

# Get a tracer for the application
tracer = trace.get_tracer(__name__)


def trace_operation(namespace=None, operation_name=None, **default_attributes):
    """
    Decorator to add OpenTelemetry tracing to 3-rd party calls.

    Usage:
        @trace_operation("get_email")
        def get_email_by_id(self, row_id):
            ...

    Args:
        operation_name: Name of the operation (defaults to function name)
        **default_attributes: Additional attributes to add to the span
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
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