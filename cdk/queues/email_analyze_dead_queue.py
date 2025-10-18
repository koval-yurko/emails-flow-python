from aws_cdk import aws_sqs as sqs, Duration
from constructs import Construct


class EmailAnalyzeDeadQueue(Construct):
    """Dead Letter Queues for failed email analyze"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DLQ for email-analyze pipeline
        self.queue = sqs.Queue(
            self,
            "Queue",
            queue_name="email-analyze-dead-queue",
            retention_period=Duration.days(10),
        )
