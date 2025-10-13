from aws_cdk import aws_sqs as sqs, Duration
from constructs import Construct


class PostStoreQueue(Construct):
    """
    Queue for post-analysis processing.

    PRODUCER: email-analyze Lambda
    CONSUMER: (none yet)
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.queue = sqs.Queue(
            self,
            "Queue",
            queue_name="post-store-queue",
            visibility_timeout=Duration.seconds(60),
            retention_period=Duration.days(5),
        )