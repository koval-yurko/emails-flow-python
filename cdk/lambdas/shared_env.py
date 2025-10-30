import os
from dotenv import load_dotenv

# Load .env file before reading environment variables
load_dotenv()

# Base environment variables shared across all Lambdas
_base_envs = {
  "AWS_LAMBDA_EXEC_WRAPPER": "/opt/otel-instrument",
  "OTEL_TRACES_SAMPLER": "always_on",  # Correct sampler name (lowercase)
  "OTEL_METRICS_EXPORTER": "otlp",  # Enable metrics export
  "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
  "OTEL_RESOURCE_ATTRIBUTES": "deployment.environment=production,service.namespace=emails-flow",
  # Disable instrumentations for libraries not used in this project
  "OTEL_PYTHON_DISABLED_INSTRUMENTATIONS": "redis,grpc,grpc_client,grpc_server,grpc_aio_client,grpc_aio_server,elasticsearch,jinja2,starlette,tornado,django,flask,fastapi,falcon,mysql,pymongo,pymysql,pyramid,pymemcache,psycopg2,asyncpg,boto,celery,aio-pika,aiohttp-client,aiohttp-server,aiopg,asgi,cassandra,confluent-kafka,dbapi,httpx,kafka-python,pika,sqlalchemy,sqlcommenter,system-metrics,threading,tornado-instrumentation,urllib,urllib3,wsgi",
  "OTEL_EXPORTER_OTLP_ENDPOINT": os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
  "OTEL_EXPORTER_OTLP_HEADERS": os.getenv("OTEL_EXPORTER_OTLP_HEADERS"),
}


# Filter out None and empty string values (CDK doesn't accept None/empty values)
envs = {k: v for k, v in _base_envs.items() if v}
