import os
from aws_cdk import (
    aws_lambda as _lambda, 
    aws_iam as iam, 
    aws_sqs as sqs, 
    aws_secretsmanager as secretsmanager,
    aws_logs as logs,
    Duration
)
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
        imap_credentials_secret: secretsmanager.Secret,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create CloudWatch Log Group with retention
        log_group = logs.LogGroup(
            self,
            "LogGroup",
            log_group_name=f"/aws/lambda/emails-flow-emails-read",
            retention=logs.RetentionDays.ONE_MONTH,
        )

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

        # Grant permission to read IMAP credentials from Secrets Manager
        imap_credentials_secret.grant_read(self.emails_read_role)

        self.function = _lambda.Function(
            self,
            "Function",
            function_name="emails-flow-emails-read",
            runtime=_lambda.Runtime.PYTHON_3_13,
            handler="main.handler",
            code=_lambda.Code.from_asset("../lambdas/1-emails-read"),
            role=self.emails_read_role,
            timeout=Duration.seconds(20),
            reserved_concurrent_executions=5,  # Rate limiting
            environment={
                "EMAIL_READ_QUEUE_URL": email_read_queue.queue_url,
                "IMAP_CREDENTIALS_SECRET_ARN": imap_credentials_secret.secret_arn,
            },
            layers=[layer],
            log_group=log_group,
        )

        # Grant permission to send messages to queue
        email_read_queue.grant_send_messages(self.emails_read_role)
        
        # Grant permission to use the queue's KMS key
        if hasattr(email_read_queue, 'encryption_master_key'):
            email_read_queue.encryption_master_key.grant_encrypt_decrypt(self.emails_read_role)