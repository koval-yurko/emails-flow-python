from aws_cdk import aws_sqs as sqs, Duration
from constructs import Construct


class EmailReadQueue(Construct):
    """
    Queue for email message IDs to be fetched and stored.

    PRODUCER: emails-read Lambda
    CONSUMER: email-store Lambda
    """

    def __init__(
        self, scope: Construct, construct_id: str, dead_letter_queue: sqs.Queue, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.queue = sqs.Queue(
            self,
            "Queue",
            queue_name="email-read-queue",
            visibility_timeout=Duration.seconds(60),
            retention_period=Duration.days(5),
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=3,  # Retry 3 times
                queue=dead_letter_queue,
            ),
        )