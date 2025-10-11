import json
import boto3

sqs = boto3.client("sqs")


def send_message(queue_url, message):
    response = sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message))

    return response
