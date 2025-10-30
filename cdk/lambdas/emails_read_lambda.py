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


class EmailsReadLambda(Construct):
    """
    PRODUCER Lambda: Fetches email IDs from IMAP and sends to queue.
    Trigger: Manual
    Sends to: email_read_queue
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        layers: Sequence[_lambda.LayerVersion],
        email_read_queue: sqs.Queue,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        function_name = "emails-flow-emails-read"

        # Create CloudWatch Log Group with retention
        log_group = logs.LogGroup(
            self,
            "LogGroup",
            log_group_name=f"/aws/lambda/{function_name}",
            retention=logs.RetentionDays.TWO_WEEKS,
        )
        Tags.of(log_group).add("app", "emails-read")

        self.emails_read_role = iam.Role(
            self,
            "Role",
            role_name="emails-flow-emails-read-lambda-role",
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
        Tags.of(self.emails_read_role).add("app", "emails-read")

        self.function = _lambda.Function(
            self,
            "Function",
            function_name=function_name,
            runtime=_lambda.Runtime.PYTHON_3_13,
            handler="main.handler",
            code=_lambda.Code.from_asset("../lambdas/1-emails-read", exclude=[".env", ".env.*", "__pycache__"]),
            role=self.emails_read_role,
            memory_size=256,
            timeout=Duration.seconds(20),
            reserved_concurrent_executions=5,  # Rate limiting
            tracing=_lambda.Tracing.ACTIVE,
            environment=envs | {
                "OTEL_SERVICE_NAME": function_name,
                "EMAIL_READ_QUEUE_URL": email_read_queue.queue_url,
                "IMAP_HOST": os.getenv("IMAP_HOST"),
                "IMAP_PORT": os.getenv("IMAP_PORT"),
                "IMAP_USER": os.getenv("IMAP_USER"),
                "IMAP_PASSWORD": os.getenv("IMAP_PASSWORD"),
            },
            layers=layers,
            log_group=log_group,
        )
        Tags.of(self.function).add("app", "emails-read")

        # Grant permission to send messages to queue
        email_read_queue.grant_send_messages(self.emails_read_role)
