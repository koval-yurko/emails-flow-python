import os
from dotenv import load_dotenv
from shared.emails import EmailService
from shared.sqs import send_message

load_dotenv()

def handler(event, context):
    print(f"Received event: '{event}'")

    folder = event.get("folder", "TLDR")
    from_filter = event.get("from_filter", "TLDR Dev <dan@tldrnewsletter.com>")

    imap_host = os.getenv("IMAP_HOST")
    imap_port = int(os.getenv("IMAP_PORT"))
    imap_user = os.getenv("IMAP_USER")
    imap_password = os.getenv("IMAP_PASSWORD")
    email_read_queue_url = os.getenv("EMAIL_READ_QUEUE_URL")

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


if __name__ == "__main__":

    class TestContext:
        function_name = "emails-read"

    handler({}, TestContext())
