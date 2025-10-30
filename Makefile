format:
	uv run black .

build_layer:
	@echo "Building Lambda layer..."
	@rm -rf dist
	@mkdir -p dist/python
	@echo "Installing dependencies for Lambda (Linux x86_64)..."
	@uv export --no-dev | uv pip install --target dist/python --python-platform linux --python-version 3.13 -r /dev/stdin
	@ln -s ../../shared dist/python/shared
	@echo "Layer structure created in dist/"

cdk_deploy: build_layer
	cd cdk && AWS_REGION=eu-central-1 cdk deploy

cdk_destroy: build_layer
	cd cdk && AWS_REGION=eu-central-1 cdk destroy

# LocalStack commands for local development
localstack-up:
	@echo "Starting LocalStack..."
	docker-compose up -d
	@echo "Waiting for LocalStack to be ready..."
	@sleep 5
	@echo "LocalStack is ready! SQS available at http://localhost:4566"

localstack-down:
	@rm -rf localstack-data
	@echo "Stopping LocalStack..."
	docker-compose down

localstack-logs:
	docker-compose logs -f localstack

localstack-stats:
	@echo "Getting SQS queue statistics..."
	AWS_ENDPOINT_URL=http://localhost:4566 aws sqs get-queue-attributes \
		--queue-url http://sqs.eu-central-1.localhost.localstack.cloud:4566/000000000000/emails-to-process \
		--attribute-names All \
		--endpoint-url http://localhost:4566 \
		--region eu-central-1

otel-logs:
	@echo "Streaming OpenTelemetry Collector logs (traces & metrics)..."
	docker logs emails-flow-otel-collector -f

otel-metrics:
	@echo "Fetching Prometheus metrics from OTEL Collector..."
	@curl -s http://localhost:8889/metrics | grep emails_flow || echo "No metrics found yet"

clean:
	rm -rf dist

clean-localstack:
	@echo "Cleaning LocalStack data and stopping containers..."
	@rm -rf localstack-data
	docker-compose down -v

.PHONY: format build_layer cdk_deploy cdk_destroy localstack-up localstack-down localstack-logs otel-logs otel-metrics localstack-test localstack-test-lambda localstack-test-lambda-sqs localstack-stats clean clean-localstack