from opentelemetry import metrics

# Get a meter for creating metrics
meter = metrics.get_meter("emails-flow")


email_store_success_counter = meter.create_counter(
    name="email_store_success",
    description="Number of successful email store operations",
    unit="1"
)
email_store_error_counter = meter.create_counter(
    name="email_store_error",
    description="Number of email store errors",
    unit="1"
)

email_analyze_success_counter = meter.create_counter(
    name="email_analyze_success",
    description="Number of successful email analyze operations",
    unit="1"
)
email_analyze_error_counter = meter.create_counter(
    name="email_analyze_error",
    description="Number of email analyze errors",
    unit="1"
)

post_store_success_counter = meter.create_counter(
    name="post_store_success",
    description="Number of successful post store operations",
    unit="1"
)
post_store_error_counter = meter.create_counter(
    name="post_store_error",
    description="Number of post store errors",
    unit="1"
)


def email_store_success_inc():
    email_store_success_counter.add(1, {"lambda": "email-store"})


def email_store_error_inc(errorType: str):
    email_store_error_counter.add(1, {"lambda": "email-store", "error_type": errorType})


def email_analyze_success_inc():
    email_analyze_success_counter.add(1, {"lambda": "email-analyze"})


def email_analyze_error_inc(errorType: str):
    email_analyze_error_counter.add(1, {"lambda": "email-analyze", "error_type": errorType})


def post_store_success_inc():
    post_store_success_counter.add(1, {"lambda": "post-store"})


def post_store_error_inc(errorType: str):
    post_store_error_counter.add(1, {"lambda": "post-store", "error_type": errorType})