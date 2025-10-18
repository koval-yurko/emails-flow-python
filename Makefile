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

clean:
	rm -rf dist

.PHONY: format build_layer cdk_deploy clean