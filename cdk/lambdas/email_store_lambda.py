import os
from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_lambda_event_sources as lambda_event_sources,
    aws_logs as logs,
    Duration,
)
from constructs import Construct


class EmailStoreLambda(Construct):
    """
    CONSUMER Lambda: Fetches emails from IMAP and stores in Supabase.
    Trigger: email_read_queue (batch_size=10, retry=3)
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        layer: _lambda.LayerVersion,
        email_read_queue: sqs.Queue,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create CloudWatch Log Group with retention
        log_group = logs.LogGroup(
            self,
            "LogGroup",
            log_group_name=f"/aws/lambda/emails-flow-email-store",
            retention=logs.RetentionDays.TWO_WEEKS,
        )

        self.email_store_role = iam.Role(
            self,
            "Role",
            role_name="emails-flow-email-store-lambda-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )

        self.function = _lambda.Function(
            self,
            "Function",
            function_name="emails-flow-email-store",
            runtime=_lambda.Runtime.PYTHON_3_13,
            handler="main.handler",
            code=_lambda.Code.from_asset("../lambdas/2-email-store"),
            role=self.email_store_role,
            timeout=Duration.seconds(20),
            reserved_concurrent_executions=10,  # Rate limiting
            environment={
                "IMAP_HOST": os.getenv("IMAP_HOST"),
                "IMAP_PORT": os.getenv("IMAP_PORT"),
                "IMAP_USER": os.getenv("IMAP_USER"),
                "IMAP_PASSWORD": os.getenv("IMAP_PASSWORD"),
                "SUPABASE_URL": os.getenv("SUPABASE_URL"),
                "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
            },
            layers=[layer],
            log_group=log_group,
        )

        # Subscribe to queue
        self.function.add_event_source(
            lambda_event_sources.SqsEventSource(
                email_read_queue,
                batch_size=10,
                max_batching_window=Duration.seconds(5),
            )
        )

        # Grant permission to consume messages
        email_read_queue.grant_consume_messages(self.function)
