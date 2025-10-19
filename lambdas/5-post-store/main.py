import os
import json
from dotenv import load_dotenv
from shared import PostMessage
from shared.supabase import SupabaseClient

load_dotenv()


def handler(event, context):
    print(f"Received {len(event['Records'])} messages from SQS")

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    supabase_client = SupabaseClient(supabase_url, supabase_key)

    batch_item_failures = []

    for record in event["Records"]:
        sqs_message_id = record["messageId"]

        try:
            body = json.loads(record["body"])

            post = PostMessage(
                email_id=body["email_id"],
                url=body["url"],
                title=body["title"],
                text=body["text"],
                domains=body.get("domains", []),
                categories=body.get("categories", []),
                tags=body.get("tags", []),
                new_tags=body.get("new_tags", []),
            )

            post_id = supabase_client.add_post(post)
            # Push Success metrics

        except Exception as e:
            print(f"Error processing message {sqs_message_id}: {str(e)}")
            batch_item_failures.append({"itemIdentifier": sqs_message_id})
            # Push Error metrics

    return {"batchItemFailures": batch_item_failures}


if __name__ == "__main__":
    handler(
        {
            "Records": [
                {
                    "messageId": "test-sqs-msg-1",
                    "body": json.dumps(
                        {
                            "email_id": "f2807cbc-e7b8-43d6-b2ba-c36a0c9e6d51",
                            "title": "Test title",
                            "text": "Test text",
                            "url": "Some URL 2",
                            "domains": ["Domain 1", "Domain 2"],
                            "categories": ["Category 1", "Category 2"],
                            "tags": ["Tag 1", "Tag 2"],
                            "new_tags": ["New Tag 1", "New Tag 2"],
                        }
                    )
                },
                {
                    "messageId": "test-sqs-msg-2",
                    "body": json.dumps(
                        {
                            "email_id": "729819c9-b1b4-4ef9-9194-d054105a38cf",
                            "title": "Test title 2",
                            "text": "Test text 2",
                            "url": "Some URL 2",
                            "domains": ["Domain 2", "Domain 3"],
                            "categories": ["Category 2", "Category 3"],
                            "tags": ["Tag 2", "Tag 3"],
                            "new_tags": ["New Tag 2", "New Tag 3"],
                        }
                    )
                },
            ]
        },
        {},
    )
