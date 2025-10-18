import os
from dotenv import load_dotenv
from shared.supabase import SupabaseClient
from shared.sqs import send_message

load_dotenv()


def handler(event, context):
    print(f"Received event: '{event}'")

    count_str = event.get("count", "1")
    count = int(count_str)

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    email_analyze_queue_url = os.getenv("EMAIL_ANALYZE_QUEUE_URL")

    supabase_client = SupabaseClient(supabase_url, supabase_key)

    rows = supabase_client.get_unprocessed_emails(count)

    for row in rows:
        send_message(
            email_analyze_queue_url,
            {"row_id": row.get("id")},
        )


if __name__ == "__main__":
    handler({"count": "1"}, {})
