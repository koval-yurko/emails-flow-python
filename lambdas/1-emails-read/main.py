import os
import json
from dotenv import load_dotenv
from shared.emails import EmailService
from shared.sqs import send_message

load_dotenv()

def handler(event, context):
    print(f"Received event: '{event}'")

    # Check if this is an API Gateway proxy integration event
    if "body" in event and "httpMethod" in event:
        # API Gateway invocation
        try:
            body = json.loads(event["body"]) if event["body"] else {}
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid JSON in request body"}),
                "headers": {"Content-Type": "application/json"},
            }

        folder = body.get("folder", "TLDR")
        from_filter = body.get("from_filter", "TLDR Dev <dan@tldrnewsletter.com>")
    else:
        # Direct Lambda invocation (manual trigger)
        folder = event.get("folder", "TLDR")
        from_filter = event.get("from_filter", "TLDR Dev <dan@tldrnewsletter.com>")

    imap_host = os.getenv("IMAP_HOST")
    imap_port = int(os.getenv("IMAP_PORT"))
    imap_user = os.getenv("IMAP_USER")
    imap_password = os.getenv("IMAP_PASSWORD")
    email_read_queue_url = os.getenv("EMAIL_READ_QUEUE_URL")

    try:
        email_server = EmailService(imap_host, imap_port, imap_user, imap_password)
        message_ids = email_server.fetch_unseen_mails(folder, from_filter)

        for msg_id in message_ids:
            send_message(
                email_read_queue_url,
                {
                    "message_id": msg_id,
                    "folder": folder,
                },
            )

        # Return success response for API Gateway
        if "body" in event and "httpMethod" in event:
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Successfully queued emails for reading",
                    "count": len(message_ids),
                    "folder": folder,
                }),
                "headers": {"Content-Type": "application/json"},
            }
    except Exception as e:
        print(f"Error: {str(e)}")
        if "body" in event and "httpMethod" in event:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"},
            }
        raise


if __name__ == "__main__":

    class TestContext:
        function_name = "emails-read"

    handler({}, TestContext())
