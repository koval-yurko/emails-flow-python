import os
from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_lambda_event_sources as lambda_event_sources,
    Duration,
)
from constructs import Construct


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
        layer: _lambda.LayerVersion,
        email_analyze_queue: sqs.Queue,
        post_store_queue: sqs.Queue,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.email_analyze_role = iam.Role(
            self,
            "EmailAnalyzeRole",
            role_name="emails-flow-email-analyze-lambda-role",
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
            function_name="emails-flow-email-analyze",
            runtime=_lambda.Runtime.PYTHON_3_13,
            handler="main.handler",
            code=_lambda.Code.from_asset("../lambdas/4-email-analyze"),
            role=self.email_analyze_role ,
            timeout=Duration.seconds(180),
            memory_size=1024,
            environment={
                "SUPABASE_URL": os.getenv("SUPABASE_URL"),
                "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
                "XAI_API_KEY": os.getenv("XAI_API_KEY"),
                "POST_STORE_QUEUE_URL": post_store_queue.queue_url,
            },
            layers=[layer],
        )

        # Subscribe to queue
        self.function.add_event_source(
            lambda_event_sources.SqsEventSource(
                email_analyze_queue,
                batch_size=1,
            )
        )

        # Grant permissions
        email_analyze_queue.grant_consume_messages(self.function)
        post_store_queue.grant_send_messages(self.email_analyze_role )