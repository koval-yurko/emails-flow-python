#!/bin/bash

# This script runs automatically when LocalStack starts up
# It initializes SQS queues for local development

echo "Creating SQS queues..."

# Create the main email processing queue
awslocal sqs create-queue \
    --queue-name emails-to-process \
    --attributes '{
        "VisibilityTimeout": "300",
        "MessageRetentionPeriod": "1209600",
        "ReceiveMessageWaitTimeSeconds": "0"
    }'

# Create a dead-letter queue for failed messages
awslocal sqs create-queue \
    --queue-name emails-to-process-dlq \
    --attributes '{
        "MessageRetentionPeriod": "1209600"
    }'

# Get queue ARNs
MAIN_QUEUE_ARN=$(awslocal sqs get-queue-attributes \
    --queue-url http://sqs.eu-central-1.localhost.localstack.cloud:4566/000000000000/emails-to-process \
    --attribute-names QueueArn \
    --query 'Attributes.QueueArn' \
    --output text)

DLQ_ARN=$(awslocal sqs get-queue-attributes \
    --queue-url http://sqs.eu-central-1.localhost.localstack.cloud:4566/000000000000/emails-to-process-dlq \
    --attribute-names QueueArn \
    --query 'Attributes.QueueArn' \
    --output text)

# Configure redrive policy (send to DLQ after 3 retries)
awslocal sqs set-queue-attributes \
    --queue-url http://sqs.eu-central-1.localhost.localstack.cloud:4566/000000000000/emails-to-process \
    --attributes '{
        "RedrivePolicy": "{\"deadLetterTargetArn\":\"'"$DLQ_ARN"'\",\"maxReceiveCount\":\"3\"}"
    }'

echo "SQS queues created successfully!"
echo "Main Queue: emails-to-process"
echo "Dead Letter Queue: emails-to-process-dlq"