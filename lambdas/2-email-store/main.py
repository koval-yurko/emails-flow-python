import os
import json
from dotenv import load_dotenv
from shared.emails import EmailService
from shared.supabase import SupabaseClient

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

    for record in event["Records"]:
        # message_id = record["messageId"]
        body = json.loads(record["body"])

        message_id = body['message_id']
        folder = body['folder']

        message = email_server.fetch_message(message_id, folder)
        supabase_client.add_email(message)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {"message": f'Successfully processed {len(event["Records"])} messages'}
        ),
    }

if __name__ == "__main__":
    handler({
        "Records": [
            {
                "body": json.dumps({
                    "message_id": "1",
                    "folder": "TLDR"
                })
            }
        ]
    }, {})