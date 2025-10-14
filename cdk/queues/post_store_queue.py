from aws_cdk import aws_sqs as sqs, aws_kms as kms, Duration
from constructs import Construct


class PostStoreQueue(Construct):
    """
    Queue for post-analysis processing.

    PRODUCER: email-analyze Lambda
    CONSUMER: (none yet)
    """

    def __init__(self, scope: Construct, construct_id: str, dead_letter_queue: sqs.Queue = None, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create KMS key for queue encryption
        self.encryption_key = kms.Key(
            self,
            "EncryptionKey",
            description="KMS key for post-store-queue encryption",
            enable_key_rotation=True,
        )

        queue_config = {
            "queue_name": "post-store-queue",
            "visibility_timeout": Duration.seconds(60),
            "retention_period": Duration.days(5),
            "encryption": sqs.QueueEncryption.KMS,
            "encryption_master_key": self.encryption_key,
        }

        # Add dead letter queue if provided
        if dead_letter_queue:
            queue_config["dead_letter_queue"] = sqs.DeadLetterQueue(
                max_receive_count=3,  # Retry 3 times
                queue=dead_letter_queue,
            )

        self.queue = sqs.Queue(
            self,
            "Queue",
            **queue_config
        )