from supabase import create_client, Client
from ..emails import EmailMessage

class SupabaseClient:
    def __init__(self, url, key):
        self.supabase: Client = create_client(url, key)

    def add_email(self, email: EmailMessage):
        current = self.supabase.from_("emails").select('*').eq("message_id", email.message_id).execute()

        if len(current.data) > 0:
            # update
            self.supabase.from_("emails").update({
                "from": email.from_email,
                "date": email.date,
                "subject": email.subject,
                "message_id": email.message_id,
                "content": email.body,
                "status": 'created'
            }).eq("message_id", email.message_id).execute()
        else:
            # insert
            self.supabase.from_("emails").insert({
                "from": email.from_email,
                "date": email.date,
                "subject": email.subject,
                "message_id": email.message_id,
                "content": email.body,
                "status": 'created'
            }).execute()

    def get_unprocessed_emails(self, count):
        resp = self.supabase.from_("emails").select("*").or_("status.eq.created,status.is.null").limit(count).execute()

        if resp.data is None:
            print("No emails found")
            return []
        return resp.data

    def get_email_by_id(self, row_id):
        resp = self.supabase.from_("emails").select("*").eq("id", row_id).execute()

        if resp.data is None:
            print("No email found")
            return None
        return resp.data[0]

    def mark_email_as_processed(self, row_id):
        self.supabase.from_("emails").update({"status": "processed"}).eq("id", row_id).execute()

