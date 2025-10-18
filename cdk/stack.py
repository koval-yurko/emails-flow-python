from aws_cdk import (
    aws_lambda as _lambda,
    App,
    Stack,
    Tags,
    CfnOutput,
)

# Import our organized modules
from queues import (
    EmailReadQueue,
    EmailReadDeadQueue,
    EmailAnalyzeQueue,
    EmailAnalyzeDeadQueue,
    PostStoreQueue,
    PostStoreDeadQueue,
)
from lambdas import (
    EmailsReadLambda,
    EmailStoreLambda,
    EmailsAnalyzeLambda,
    EmailAnalyzeLambda,
    PostStoreLambda,
)


class PythonLambdaStack(Stack):
    """
    EMAIL PROCESSING PIPELINE:

    PIPELINE 1: Email Reading & Storage
    -----------------------------------
    1. emails-read Lambda (manual) → email_read_queue
    2. email_read_queue → email-store Lambda (SQS trigger)

    PIPELINE 2: Email Analysis
    ---------------------------
    3. emails-analyze Lambda (manual) → email_analyze_queue
    4. email_analyze_queue → email-analyze Lambda (SQS trigger) → post_store_queue
    """

    def __init__(self, app: App, id: str, **kwargs) -> None:
        super().__init__(app, id, **kwargs)

        # Tags
        Tags.of(self).add("app", "emails-flow")
        Tags.of(self).add("env", "test")

        # ========================================
        # 1. SHARED RESOURCES
        # ========================================

        # Lambda Layer with shared code
        shared_layer = _lambda.LayerVersion(
            self,
            "SharedLayer",
            code=_lambda.Code.from_asset("../dist"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_13],
            description="Shared code for emails-flow lambdas",
        )

        # ========================================
        # 2. QUEUES
        # ========================================

        # Queue for email IDs
        email_read_dead_queue = EmailReadDeadQueue(self, "EmailReadDeadQueue")
        email_read_queue = EmailReadQueue(
            self, "EmailReadQueue", dead_letter_queue=email_read_dead_queue.queue
        )

        # Queue for email analysis
        email_analyze_dead_queue = EmailAnalyzeDeadQueue(
            self,
            "EmailAnalyzeDeadQueue",
        )
        email_analyze_queue = EmailAnalyzeQueue(
            self, "EmailAnalyzeQueue", dead_letter_queue=email_analyze_dead_queue.queue
        )

        # Queue for post-storage processing
        post_store_dead_queue = PostStoreDeadQueue(self, "PostStoreDeadQueue")
        post_store_queue = PostStoreQueue(
            self, "PostStoreQueue", dead_letter_queue=post_store_dead_queue.queue
        )

        # ========================================
        # 3. LAMBDAS
        # ========================================

        # PRODUCER: Fetch email IDs from IMAP → email_read_queue
        emails_read = EmailsReadLambda(
            self,
            "EmailsReadLambda",
            layer=shared_layer,
            email_read_queue=email_read_queue.queue,
        )

        # CONSUMER: email_read_queue → Store emails in Supabase
        email_store = EmailStoreLambda(
            self,
            "EmailStoreLambda",
            layer=shared_layer,
            email_read_queue=email_read_queue.queue,
        )

        # PRODUCER: Query Supabase → email_analyze_queue
        emails_analyze = EmailsAnalyzeLambda(
            self,
            "EmailsAnalyzeLambda",
            layer=shared_layer,
            email_analyze_queue=email_analyze_queue.queue,
        )

        # CONSUMER: email_analyze_queue → Analyze → post_store_queue
        email_analyze = EmailAnalyzeLambda(
            self,
            "EmailAnalyzeLambda",
            layer=shared_layer,
            email_analyze_queue=email_analyze_queue.queue,
            post_store_queue=post_store_queue.queue,
        )

        # CONSUMER: email_analyze_queue → Analyze → post_store_queue
        post_store = PostStoreLambda(
            self,
            "EmailAnalyzeLambda",
            layer=shared_layer,
            post_store_queue=post_store_queue.queue,
        )

        # ========================================
        # 4. OUTPUTS
        # ========================================

        CfnOutput(
            self,
            "EmailsReadLambdaArn",
            value=emails_read.function.function_arn,
            export_name="EmailsFlowMainLambdaArn",
        )

        CfnOutput(
            self,
            "EmailStoreLambdaArn",
            value=email_store.function.function_arn,
            export_name="EmailsFlowConsumerLambdaArn",
        )

        CfnOutput(
            self,
            "EmailAnalyzeLambdaArn",
            value=email_analyze.function.function_arn,
            export_name="EmailsFlowAnalyzeLambdaArn",
        )

        CfnOutput(
            self,
            "EmailsAnalyzeLambdaArn",
            value=emails_analyze.function.function_arn,
            export_name="EmailsFlowEmailsAnalyzeLambdaArn",
        )

        CfnOutput(
            self,
            "PostStoreLambdaArn",
            value=post_store.function.function_arn,
            export_name="EmailsFlowPostStoreLambdaArn",
        )

        CfnOutput(
            self,
            "EmailReadQueueUrl",
            value=email_read_queue.queue.queue_url,
            export_name="EmailReadQueueUrl",
        )

        CfnOutput(
            self,
            "EmailAnalyzeQueueUrl",
            value=email_analyze_queue.queue.queue_url,
            export_name="EmailAnalyzeQueueUrl",
        )

        CfnOutput(
            self,
            "PostStoreQueueUrl",
            value=post_store_queue.queue.queue_url,
            export_name="PostStoreQueueUrl",
        )
