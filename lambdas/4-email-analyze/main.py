import os
import json
from dotenv import load_dotenv
from shared.supabase import SupabaseClient
from shared.emails import clean_html
from shared.ai import LLMEngine
from shared.sqs import send_message

load_dotenv()


def handler(event, context):
    print(f"Received {len(event['Records'])} messages from SQS")

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    post_store_queue_url = os.getenv("POST_STORE_QUEUE_URL")

    supabase_client = SupabaseClient(supabase_url, supabase_key)

    llm = LLMEngine()

    batch_item_failures = []

    for record in event["Records"]:
        sqs_message_id = record["messageId"]

        try:
            body = json.loads(record["body"])
            row_id = body["row_id"]

            email = supabase_client.get_email_by_id(row_id)

            content = email["clean_content"]

            posts = llm.get_email_summary(content)

            # send results to post-store
            for post in posts:
                send_message(
                    post_store_queue_url,
                    {
                        "email_id": row_id,
                        "title": post.title,
                        "url": post.url,
                        "text": post.text,
                        "domains": post.domains,
                        "categories": post.categories,
                        "tags": post.tags,
                        "new_tags": post.newTags,
                    },
                )

            supabase_client.mark_email_as_processed(row_id)
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
                            "row_id": "027e3b3b-db82-4db4-9f0b-de733198b25c",
                        }
                    ),
                }
            ]
        },
        {},
    )
