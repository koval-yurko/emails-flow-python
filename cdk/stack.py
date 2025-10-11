from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_lambda_event_sources as lambda_event_sources,
    App,
    Stack,
    Tags,
    CfnOutput,
    Duration,
)
import os


class PythonLambdaStack(Stack):
    def __init__(self, app: App, id: str, **kwargs) -> None:
        super().__init__(app, id, **kwargs)

        # Add tags to all resources in this stack
        Tags.of(self).add("app", "emails-flow")
        Tags.of(self).add("env", "test")

        # Create Dead Letter Queue
        dead_letter_queue = sqs.Queue(
            self,
            "emails-flow-dlq",
            queue_name="emails-flow-dead-queue",
            retention_period=Duration.days(14),
        )

        # Create SQS queue with DLQ
        email_read_queue = sqs.Queue(
            self,
            "emails-flow-queue",
            queue_name="emails-flow-queue",
            visibility_timeout=Duration.seconds(60),  # 1 minute timeout for message handling
            retention_period=Duration.days(5),
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=3,  # Retry 3 times before moving to DLQ
                queue=dead_letter_queue,
            ),
        )

        emails_read_lambda_role = iam.Role(
            self,
            "emails-flow-lambda-role",
            role_name="emails-flow-lambda-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )

        # Create Lambda Layer with shared code
        shared_layer = _lambda.LayerVersion(
            self,
            "emails-flow-shared-layer",
            code=_lambda.Code.from_asset("../dist"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_13],
            description="Shared code for emails-flow lambdas",
        )

        emails_read_lambda = _lambda.Function(
            self,
            "emails-flow-main",
            function_name="emails-flow-main",
            runtime=_lambda.Runtime.PYTHON_3_13,
            handler="main.handler",
            code=_lambda.Code.from_asset("../lambdas/emails-read"),
            role=emails_read_lambda_role,
            timeout=Duration.seconds(20),
            environment={
                "SQS_QUEUE_URL": email_read_queue.queue_url,
                "IMAP_HOST": os.getenv('IMAP_HOST'),
                "IMAP_PORT": os.getenv('IMAP_PORT'),
                "IMAP_USER": os.getenv('IMAP_USER'),
                "IMAP_PASSWORD": os.getenv('IMAP_PASSWORD'),
            },
            layers=[shared_layer],
        )

        # Grant Lambda permission to send messages to SQS
        email_read_queue.grant_send_messages(emails_read_lambda_role)

        # Create consumer Lambda role
        consumer_lambda_role = iam.Role(
            self,
            "emails-flow-consumer-lambda-role",
            role_name="emails-flow-consumer-lambda-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )

        # Create consumer Lambda function
        consumer_function = _lambda.Function(
            self,
            "emails-flow-consumer",
            function_name="emails-flow-consumer",
            runtime=_lambda.Runtime.PYTHON_3_13,
            handler="main.handler",
            code=_lambda.Code.from_asset("../lambdas/email-read"),
            timeout=Duration.seconds(20),
            role=consumer_lambda_role,
            environment={
                "IMAP_HOST": os.getenv('IMAP_HOST'),
                "IMAP_PORT": os.getenv('IMAP_PORT'),
                "IMAP_USER": os.getenv('IMAP_USER'),
                "IMAP_PASSWORD": os.getenv('IMAP_PASSWORD'),
                "SUPABASE_URL": os.getenv('SUPABASE_URL'),
                "SUPABASE_KEY": os.getenv('SUPABASE_KEY'),
            },
            layers=[shared_layer],
        )

        # Add SQS as event source for consumer Lambda
        consumer_function.add_event_source(
            lambda_event_sources.SqsEventSource(
                email_read_queue,
                batch_size=10,  # Process up to 10 messages at once
                max_batching_window=Duration.seconds(
                    5
                ),  # Wait up to 5 seconds to batch messages
            )
        )

        # Grant consumer Lambda permission to consume messages from SQS
        email_read_queue.grant_consume_messages(consumer_function)

        # Output Lambda ARN
        CfnOutput(
            self,
            "EmailsFlowLambdaArn",
            value=emails_read_lambda.function_arn,
            description="ARN of the emails-flow Lambda function",
            export_name="EmailsFlowLambdaArn",
        )

        # Output SQS Queue URL
        CfnOutput(
            self,
            "EmailsFlowQueueUrl",
            value=email_read_queue.queue_url,
            description="URL of the emails-flow SQS queue",
            export_name="EmailsFlowQueueUrl",
        )

        # Output Consumer Lambda ARN
        CfnOutput(
            self,
            "EmailsFlowConsumerLambdaArn",
            value=consumer_function.function_arn,
            description="ARN of the emails-flow consumer Lambda function",
            export_name="EmailsFlowConsumerLambdaArn",
        )

        # Output DLQ URL
        CfnOutput(
            self,
            "EmailsFlowDLQUrl",
            value=dead_letter_queue.queue_url,
            description="URL of the emails-flow Dead Letter Queue",
            export_name="EmailsFlowDLQUrl",
        )
