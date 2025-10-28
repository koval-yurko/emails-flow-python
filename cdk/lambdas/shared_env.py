import os
from dotenv import load_dotenv

# Load .env file before reading environment variables
load_dotenv()

# Base environment variables shared across all Lambdas
envs = {
  "AWS_LAMBDA_EXEC_WRAPPER": "/opt/otel-instrument",
  "OTEL_TRACES_SAMPLER": "AlwaysOn",
  "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
  "OTEL_RESOURCE_ATTRIBUTES": "deployment.environment=test,service.namespace=emails-flow",
  "OTEL_PYTHON_DISABLED_INSTRUMENTATIONS": "redis,starlette,tornado,django,flask,fastapi,falcon",
  "OTEL_EXPORTER_OTLP_ENDPOINT": os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
  "OTEL_EXPORTER_OTLP_HEADERS": os.getenv("OTEL_EXPORTER_OTLP_HEADERS"),
  "GRAFANA_INSTANCE_ID": os.getenv("GRAFANA_INSTANCE_ID"),
}
