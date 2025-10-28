import os
from typing import Sequence

from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_lambda_event_sources as lambda_event_sources,
    aws_logs as logs,
    Duration,
    Tags,
)
from constructs import Construct
from .shared_env import envs


class EmailAnalyzeLambda(Construct):
    """
    CONSUMER Lambda: Analyzes emails and sends results.
    Trigger: email_analyze_queue (batch_size=1, retry=1)
    Sends to: post_store_queue
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        layers: Sequence[_lambda.LayerVersion],
        email_analyze_queue: sqs.Queue,
        post_store_queue: sqs.Queue,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        function_name = "emails-flow-email-analyze"

        # Create CloudWatch Log Group with retention
        log_group = logs.LogGroup(
            self,
            "LogGroup",
            log_group_name=f"/aws/lambda/{function_name}",
            retention=logs.RetentionDays.TWO_WEEKS,
        )
        Tags.of(log_group).add("app", "email-analyze")

        self.email_analyze_role = iam.Role(
            self,
            "Role",
            role_name="emails-flow-email-analyze-lambda-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AWSXRayDaemonWriteAccess"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "CloudWatchFullAccess"
                ),
            ],
        )
        Tags.of(self.email_analyze_role).add("app", "email-analyze")

        self.function = _lambda.Function(
            self,
            "Function",
            function_name=function_name,
            runtime=_lambda.Runtime.PYTHON_3_13,
            handler="main.handler",
            code=_lambda.Code.from_asset("../lambdas/4-email-analyze"),
            role=self.email_analyze_role,
            timeout=Duration.seconds(180),
            memory_size=1024,
            reserved_concurrent_executions=3,  # Rate limiting
            tracing=_lambda.Tracing.ACTIVE,
            environment=envs | {
                "OTEL_SERVICE_NAME": function_name,
                "SUPABASE_URL": os.getenv("SUPABASE_URL"),
                "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
                "XAI_API_KEY": os.getenv("XAI_API_KEY"),
                "POST_STORE_QUEUE_URL": post_store_queue.queue_url,
            },
            layers=layers,
            log_group=log_group,
        )
        Tags.of(self.function).add("app", "email-analyze")

        # Subscribe to queue
        self.function.add_event_source(
            lambda_event_sources.SqsEventSource(
                email_analyze_queue,
                batch_size=1,
                report_batch_item_failures=True,
            )
        )

        # Grant permissions
        email_analyze_queue.grant_consume_messages(self.function)
        post_store_queue.grant_send_messages(self.email_analyze_role)
