import os
import json
from dotenv import load_dotenv
from shared.emails import EmailService, clean_html
from shared.supabase import SupabaseClient
from shared.metrics import email_store_success_inc, email_store_error_inc

load_dotenv()

def handler(event, context):
    print(f"Received {len(event['Records'])} messages from SQS")

    imap_host = os.getenv("IMAP_HOST")
    imap_port = int(os.getenv("IMAP_PORT"))
    imap_user = os.getenv("IMAP_USER")
    imap_password = os.getenv("IMAP_PASSWORD")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    email_server = EmailService(imap_host, imap_port, imap_user, imap_password)

    supabase_client = SupabaseClient(supabase_url, supabase_key)

    batch_item_failures = []

    for record in event["Records"]:
        sqs_message_id = record["messageId"]

        try:
            body = json.loads(record["body"])

            message_id = body["message_id"]
            folder = body["folder"]

            message = email_server.fetch_message(message_id, folder)

            clean_content = clean_html(message.body)
            supabase_client.add_email(message, clean_content)

            email_server.mark_massage_as_seen(message_id, folder)

            email_store_success_inc()

        except Exception as e:
            print(f"Error processing message {sqs_message_id}: {str(e)}")
            batch_item_failures.append({"itemIdentifier": sqs_message_id})

            email_store_error_inc(type(e).__name__)

    return {"batchItemFailures": batch_item_failures}


if __name__ == "__main__":
    handler(
        {
            "Records": [
                {
                    "messageId": "test-sqs-msg-1",
                    "body": json.dumps({"message_id": "1", "folder": "TLDR"}),
                }
            ]
        },
        {},
    )
