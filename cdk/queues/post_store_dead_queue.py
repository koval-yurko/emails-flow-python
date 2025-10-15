from aws_cdk import aws_sqs as sqs, Duration
from constructs import Construct


class PostStoreDeadQueue(Construct):
    """Dead Letter Queue for failed post-store processing"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DLQ for post-store pipeline
        self.queue = sqs.Queue(
            self,
            "PostStoreDLQ",
            queue_name="post-store-dead-queue",
            retention_period=Duration.days(10),
        )