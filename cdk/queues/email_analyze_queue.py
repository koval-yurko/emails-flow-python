from aws_cdk import aws_sqs as sqs, aws_kms as kms, Duration
from constructs import Construct


class EmailAnalyzeQueue(Construct):
    """
    Queue for emails to be analyzed.

    PRODUCER: emails-analyze Lambda
    CONSUMER: email-analyze Lambda
    """

    def __init__(
        self, scope: Construct, construct_id: str, dead_letter_queue: sqs.Queue, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create KMS key for queue encryption
        self.encryption_key = kms.Key(
            self,
            "EncryptionKey",
            description="KMS key for email-analyze-queue encryption",
            enable_key_rotation=True,
        )

        self.queue = sqs.Queue(
            self,
            "Queue",
            queue_name="email-analyze-queue",
            visibility_timeout=Duration.seconds(60),
            retention_period=Duration.days(5),
            encryption=sqs.QueueEncryption.KMS,
            encryption_master_key=self.encryption_key,
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=1,  # Retry 1 time
                queue=dead_letter_queue,
            ),
        )