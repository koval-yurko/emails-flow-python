import os
from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_logs as logs,
    Duration,
)
from constructs import Construct


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
        layer: _lambda.LayerVersion,
        email_analyze_queue: sqs.Queue,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create CloudWatch Log Group with retention
        log_group = logs.LogGroup(
            self,
            "LogGroup",
            log_group_name=f"/aws/lambda/emails-flow-emails-analyze",
            retention=logs.RetentionDays.TWO_WEEKS,
        )

        # Role for emails-analyze Lambda (PRODUCER)
        self.emails_analyze_role = iam.Role(
            self,
            "Role",
            role_name="emails-flow-emails-analyze-lambda-role",
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
            function_name="emails-flow-emails-analyze",
            runtime=_lambda.Runtime.PYTHON_3_13,
            handler="main.handler",
            code=_lambda.Code.from_asset("../lambdas/3-emails-analyze"),
            role=self.emails_analyze_role,
            timeout=Duration.seconds(60),
            reserved_concurrent_executions=5,  # Rate limiting
            environment={
                "EMAIL_ANALYZE_QUEUE_URL": email_analyze_queue.queue_url,
                "SUPABASE_URL": os.getenv("SUPABASE_URL"),
                "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
            },
            layers=[layer],
            log_group=log_group,
        )

        # Grant permission to send messages to queue
        email_analyze_queue.grant_send_messages(self.emails_analyze_role)
