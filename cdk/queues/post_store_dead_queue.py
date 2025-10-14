from aws_cdk import aws_sqs as sqs, aws_kms as kms, Duration
from constructs import Construct


class PostStoreDeadQueue(Construct):
    """Dead Letter Queue for failed post-store processing"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create KMS key for dead letter queue encryption
        self.encryption_key = kms.Key(
            self,
            "EncryptionKey",
            description="KMS key for post-store-dead-queue encryption",
            enable_key_rotation=True,
        )

        # DLQ for post-store pipeline
        self.queue = sqs.Queue(
            self,
            "PostStoreDLQ",
            queue_name="post-store-dead-queue",
            retention_period=Duration.days(10),
            encryption=sqs.QueueEncryption.KMS,
            encryption_master_key=self.encryption_key,
        )