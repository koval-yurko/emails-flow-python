import os
from aws_cdk import aws_lambda as _lambda, aws_iam as iam, aws_sqs as sqs, Duration
from constructs import Construct


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
        layer: _lambda.LayerVersion,
        email_read_queue: sqs.Queue,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.emails_read_role = iam.Role(
            self,
            "EmailsReadRole",
            role_name="emails-flow-emails-read-lambda-role",
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
            function_name="emails-flow-emails-read",
            runtime=_lambda.Runtime.PYTHON_3_13,
            handler="main.handler",
            code=_lambda.Code.from_asset("../lambdas/1-emails-read"),
            role=self.emails_read_role,
            timeout=Duration.seconds(20),
            environment={
                "EMAIL_READ_QUEUE_URL": email_read_queue.queue_url,
                "IMAP_HOST": os.getenv("IMAP_HOST"),
                "IMAP_PORT": os.getenv("IMAP_PORT"),
                "IMAP_USER": os.getenv("IMAP_USER"),
                "IMAP_PASSWORD": os.getenv("IMAP_PASSWORD"),
            },
            layers=[layer],
        )

        # Grant permission to send messages to queue
        email_read_queue.grant_send_messages(self.emails_read_role)