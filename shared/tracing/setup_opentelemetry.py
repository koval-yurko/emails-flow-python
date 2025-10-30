import os
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor

def parse_headers(headers_str):
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

def setup_opentelemetry():
    """Initialize OpenTelemetry for Lambda"""

    # Create resource with service information
    resource = Resource.create({
        "service.name": os.environ.get("OTEL_SERVICE_NAME", "lambda-function"),
        "service.version": os.environ.get("SERVICE_VERSION", "1.0.0"),
        "deployment.environment": os.environ.get("ENVIRONMENT", "production"),
    })

    # Get endpoint and headers
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    headers_str = os.environ.get("OTEL_EXPORTER_OTLP_HEADERS")

    if not endpoint:
        print("OTEL_EXPORTER_OTLP_ENDPOINT not set, skipping OpenTelemetry setup")
        return

    # Parse headers
    headers = parse_headers(headers_str)

    print(f"Setting up OpenTelemetry with endpoint: {endpoint}")
    print(f"Environment: {os.environ.get('ENVIRONMENT', 'production')}")
    print(f"Service: {os.environ.get('OTEL_SERVICE_NAME', 'lambda-function')}")

    # ===== TRACING SETUP =====
    trace_provider = TracerProvider(resource=resource)
    otlp_trace_exporter = OTLPSpanExporter(
        endpoint=endpoint,
        headers=headers,
    )
    trace_provider.add_span_processor(BatchSpanProcessor(otlp_trace_exporter))
    trace.set_tracer_provider(trace_provider)

    # ===== METRICS SETUP =====
    otlp_metric_exporter = OTLPMetricExporter(
        endpoint=endpoint,
        headers=headers,
    )
    metric_reader = PeriodicExportingMetricReader(otlp_metric_exporter)
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    # ===== AUTO-INSTRUMENTATION =====
    BotocoreInstrumentor().instrument()