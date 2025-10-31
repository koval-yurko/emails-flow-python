from opentelemetry import metrics

# Get a meter for creating metrics
meter = metrics.get_meter("emails-flow")

test_success_counter = meter.create_counter(name="yura_test_success", unit="1")
test_error_counter = meter.create_counter(name="yura_test_error", unit="1")


def test_success_inc(retry_count: str | None = None):
    attributes = {
        "lambda": "test-lambda",
        "retry_count": retry_count if retry_count is not None else "0",
    }
    test_success_counter.add(1, attributes)


def test_error_inc(errorType: str | None = None, retry_count: str | None = None):
    attributes = {
        "lambda": "test-lambda",
        "error_type": errorType if errorType is not None else "",
        "retry_count": retry_count if retry_count is not None else "0",
    }
    test_error_counter.add(1, attributes)


email_store_success_counter = meter.create_counter(
    name="email_store_success",
    description="Number of successful email store operations",
    unit="1",
)
email_store_error_counter = meter.create_counter(
    name="email_store_error", description="Number of email store errors", unit="1"
)

email_analyze_success_counter = meter.create_counter(
    name="email_analyze_success",
    description="Number of successful email analyze operations",
    unit="1",
)
email_analyze_error_counter = meter.create_counter(
    name="email_analyze_error", description="Number of email analyze errors", unit="1"
)

post_store_success_counter = meter.create_counter(
    name="post_store_success",
    description="Number of successful post store operations",
    unit="1",
)
post_store_error_counter = meter.create_counter(
    name="post_store_error", description="Number of post store errors", unit="1"
)


def email_store_success_inc(retry_count: str | None = None):
    attributes = {
        "lambda": "email-store",
        "retry_count": retry_count if retry_count is not None else "0",
    }
    email_store_success_counter.add(1, attributes)


def email_store_error_inc(errorType: str, retry_count: str | None = None):
    attributes = {
        "lambda": "email-store",
        "error_type": errorType,
        "retry_count": retry_count if retry_count is not None else "0",
    }
    email_store_error_counter.add(1, attributes)


def email_analyze_success_inc(retry_count: str | None = None):
    attributes = {
        "lambda": "email-analyze",
        "retry_count": retry_count if retry_count is not None else "0",
    }
    email_analyze_success_counter.add(1, attributes)


def email_analyze_error_inc(errorType: str, retry_count: str | None = None):
    attributes = {
        "lambda": "email-analyze",
        "error_type": errorType,
        "retry_count": retry_count if retry_count is not None else "0",
    }
    email_analyze_error_counter.add(1, attributes)


def post_store_success_inc(retry_count: str | None = None):
    attributes = {
        "lambda": "post-store",
        "retry_count": retry_count if retry_count is not None else "0",
    }
    post_store_success_counter.add(1, attributes)


def post_store_error_inc(errorType: str, retry_count: str | None = None):
    attributes = {
        "lambda": "post-store",
        "error_type": errorType,
        "retry_count": retry_count if retry_count is not None else "0",
    }
    post_store_error_counter.add(1, attributes)
