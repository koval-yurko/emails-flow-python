import json
import os
import boto3

# Support LocalStack for local development
endpoint_url = os.getenv("AWS_ENDPOINT_URL")
region = os.getenv("AWS_REGION", "eu-central-1")

if endpoint_url is not None:
    print(f"Using LocalStack endpoint: {endpoint_url}")
    sqs = boto3.client(
        "sqs",
        endpoint_url=endpoint_url,
        region_name=region
    )
else:
    sqs = boto3.client("sqs")


def send_message(queue_url, message):
    response = sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message))

    return response
