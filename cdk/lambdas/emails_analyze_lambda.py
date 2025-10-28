import os
from typing import Sequence

from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_logs as logs,
    Duration,
    Tags,
)
from constructs import Construct
from .shared_env import envs


class EmailsAnalyzeLambda(Construct):
    """
    PRODUCER Lambda: Queries Supabase for unprocessed emails and queues them.
    Trigger: Manual
    Sends to: email_analyze_queue
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        layers: Sequence[_lambda.LayerVersion],
        email_analyze_queue: sqs.Queue,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        function_name = "emails-flow-emails-analyze"

        # Create CloudWatch Log Group with retention
        log_group = logs.LogGroup(
            self,
            "LogGroup",
            log_group_name=f"/aws/lambda/{function_name}",
            retention=logs.RetentionDays.TWO_WEEKS,
        )
        Tags.of(log_group).add("app", "emails-analyze")

        # Role for emails-analyze Lambda (PRODUCER)
        self.emails_analyze_role = iam.Role(
            self,
            "Role",
            role_name="emails-flow-emails-analyze-lambda-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AWSXRayDaemonWriteAccess"
                ),
            ],
        )
        Tags.of(self.emails_analyze_role).add("app", "emails-analyze")

        self.function = _lambda.Function(
            self,
            "Function",
            function_name=function_name,
            runtime=_lambda.Runtime.PYTHON_3_13,
            handler="main.handler",
            code=_lambda.Code.from_asset("../lambdas/3-emails-analyze"),
            role=self.emails_analyze_role,
            timeout=Duration.seconds(60),
            memory_size=256,
            reserved_concurrent_executions=5,  # Rate limiting
            tracing=_lambda.Tracing.ACTIVE,
            environment=envs | {
                "OTEL_SERVICE_NAME": function_name,
                "EMAIL_ANALYZE_QUEUE_URL": email_analyze_queue.queue_url,
                "SUPABASE_URL": os.getenv("SUPABASE_URL"),
                "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
            },
            layers=layers,
            log_group=log_group,
        )
        Tags.of(self.function).add("app", "emails-analyze")

        # Grant permission to send messages to queue
        email_analyze_queue.grant_send_messages(self.emails_analyze_role)
