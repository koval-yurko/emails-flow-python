import os
from dotenv import load_dotenv

# Load .env file before reading environment variables
load_dotenv()

# Base environment variables shared across all Lambdas
_base_envs = {
  "AWS_LAMBDA_EXEC_WRAPPER": "/opt/otel-instrument",
  "OTEL_TRACES_SAMPLER": "AlwaysOn",
  "OTEL_METRICS_EXPORTER": "otlp",  # Enable metrics export
  "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
  "OTEL_RESOURCE_ATTRIBUTES": "deployment.environment=test,service.namespace=emails-flow",
  "OTEL_PYTHON_DISABLED_INSTRUMENTATIONS": "redis,grpc,grpc_client,grpc_server,grpc_aio_client,grpc_aio_server,elasticsearch,jinja2,starlette,tornado,django,flask,fastapi,falcon,mysql,pymongo,pymysql,pyramid,pymemcache,psycopg2",
  "OTEL_EXPORTER_OTLP_ENDPOINT": os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
  "OTEL_EXPORTER_OTLP_HEADERS": os.getenv("OTEL_EXPORTER_OTLP_HEADERS"),
  "GRAFANA_INSTANCE_ID": os.getenv("GRAFANA_INSTANCE_ID"),
}

# Filter out None and empty string values (CDK doesn't accept None/empty values)
envs = {k: v for k, v in _base_envs.items() if v}
