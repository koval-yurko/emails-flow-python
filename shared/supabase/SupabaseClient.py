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
            }).eq("message_id", email.message_id).execute()
        else:
            # insert
            self.supabase.from_("emails").insert({
                "from": email.from_email,
                "date": email.date,
                "subject": email.subject,
                "message_id": email.message_id,
                "content": email.body,
            }).execute()
