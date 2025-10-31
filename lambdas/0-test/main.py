import os
import time
from dotenv import load_dotenv
from shared.emails import EmailService
from shared.sqs import send_message
from shared.metrics import test_success_inc, test_error_inc

load_dotenv()


def handler(event, context):
    print(f"Received event: '{event}'")

    time.sleep(0.5)
    test_success_inc()
    time.sleep(0.5)
    test_success_inc("0")
    time.sleep(0.5)
    test_success_inc("0")
    time.sleep(0.5)
    test_success_inc("1")
    time.sleep(0.5)
    test_success_inc("2")

    time.sleep(0.5)
    test_error_inc()
    time.sleep(0.5)
    test_error_inc("Error1", "0")
    time.sleep(0.5)
    test_error_inc("Error2", "0")
    time.sleep(0.5)
    test_error_inc("Error2", "1")
    time.sleep(0.5)
    test_error_inc("Error1", "2")


if __name__ == "__main__":

    class TestContext:
        function_name = "emails-read"

    handler({}, TestContext())
