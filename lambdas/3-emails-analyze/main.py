import os
import json
from dotenv import load_dotenv
from shared.supabase import SupabaseClient
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

        count_str = body.get("count", "1")
    else:
        # Direct Lambda invocation (manual trigger)
        count_str = event.get("count", "1")

    count = int(count_str)

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    email_analyze_queue_url = os.getenv("EMAIL_ANALYZE_QUEUE_URL")

    try:
        supabase_client = SupabaseClient(supabase_url, supabase_key)

        rows = supabase_client.get_unprocessed_emails(count)

        for row in rows:
            send_message(
                email_analyze_queue_url,
                {"row_id": row.get("id")},
            )

        # Return success response for API Gateway
        if "body" in event and "httpMethod" in event:
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Successfully queued emails for analysis",
                    "count": len(rows),
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
    handler({"count": "1"}, {})
