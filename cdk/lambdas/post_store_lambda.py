import os
from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_logs as logs,
    aws_lambda_event_sources as lambda_event_sources,
    Duration,
)
from constructs import Construct


class PostStoreLambda(Construct):
    """
    CONSUMER Lambda: Store posts.
    Trigger: post_store_queue (batch_size=10, retry=2)
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        layer: _lambda.LayerVersion,
        post_store_queue: sqs.Queue,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create CloudWatch Log Group with retention
        log_group = logs.LogGroup(
            self,
            "LogGroup",
            log_group_name=f"/aws/lambda/emails-flow-post-store",
            retention=logs.RetentionDays.TWO_WEEKS,
        )

        self.post_store_role = iam.Role(
            self,
            "Role",
            role_name="emails-flow-post-store-lambda-role",
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
            function_name="emails-flow-post-store",
            runtime=_lambda.Runtime.PYTHON_3_13,
            handler="main.handler",
            code=_lambda.Code.from_asset("../lambdas/5-post-store"),
            role=self.post_store_role,
            timeout=Duration.seconds(60),
            memory_size=256,
            reserved_concurrent_executions=10,
            environment={
                "SUPABASE_URL": os.getenv("SUPABASE_URL"),
                "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
            },
            layers=[layer],
            log_group=log_group,
        )

        # Subscribe to queue
        self.function.add_event_source(
            lambda_event_sources.SqsEventSource(
                post_store_queue,
                batch_size=10,
                max_batching_window=Duration.seconds(5),
                report_batch_item_failures=True,
            )
        )

        # Grant permissions
        post_store_queue.grant_consume_messages(self.function)
