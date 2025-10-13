from aws_cdk import aws_sqs as sqs, Duration
from constructs import Construct


class EmailReadDeadQueue(Construct):
    """Dead Letter Queue for failed email read"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DLQ for email-read pipeline
        self.queue = sqs.Queue(
            self,
            "EmailReadDLQ",
            queue_name="email-read-dead-queue",
            retention_period=Duration.days(10),
        )