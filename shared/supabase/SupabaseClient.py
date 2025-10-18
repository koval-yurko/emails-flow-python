from supabase import create_client, Client
from shared import EmailMessage, PostMessage


class SupabaseClient:
    def __init__(self, url, key):
        self.supabase: Client = create_client(url, key)

    def add_email(self, email: EmailMessage, clean_content: str):
        current = (
            self.supabase.from_("emails")
            .select("*")
            .eq("message_id", email.message_id)
            .execute()
        )

        if len(current.data) > 0:
            # update
            self.supabase.from_("emails").update(
                {
                    "from": email.from_email,
                    "date": email.date,
                    "subject": email.subject,
                    "message_id": email.message_id,
                    "content": email.body,
                    "clean_content": clean_content,
                    "status": "created",
                }
            ).eq("message_id", email.message_id).execute()
        else:
            # insert
            self.supabase.from_("emails").insert(
                {
                    "from": email.from_email,
                    "date": email.date,
                    "subject": email.subject,
                    "message_id": email.message_id,
                    "content": email.body,
                    "clean_content": clean_content,
                    "status": "created",
                }
            ).execute()

    def get_unprocessed_emails(self, count):
        resp = (
            self.supabase.from_("emails")
            .select("*")
            .or_("status.eq.created,status.is.null")
            .limit(count)
            .execute()
        )

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
        self.supabase.from_("emails").update({"status": "processed"}).eq(
            "id", row_id
        ).execute()

    def add_post(self, post: PostMessage):
        domains_ids = [
            self.get_or_create_tag(domain, "domain") for domain in post.domains
        ]
        categories_ids = [
            self.get_or_create_tag(category, "category") for category in post.categories
        ]
        tags_ids = [self.get_or_create_tag(tag, "tag") for tag in post.tags]
        new_tags_ids = [self.get_or_create_tag(tag, "tag_new") for tag in post.new_tags]

        current = self.supabase.from_("posts").select("*").eq("url", post.url).execute()

        post_id = ""

        if len(current.data) > 0:
            # update
            res = (
                self.supabase.from_("posts")
                .update(
                    {
                        "email_id": post.email_id,
                        "title": post.title,
                        "text": post.text,
                    }
                )
                .eq("url", post.url)
                .execute()
            )

            post_id = res.data[0]["id"]
        else:
            # insert
            res = (
                self.supabase.from_("posts")
                .insert(
                    {
                        "email_id": post.email_id,
                        "url": post.url,
                        "title": post.title,
                        "text": post.text,
                    }
                )
                .execute()
            )
            post_id = res.data[0]["id"]

        # link tags
        self.link_post_to_tags(post_id, domains_ids)
        self.link_post_to_tags(post_id, categories_ids)
        self.link_post_to_tags(post_id, tags_ids)
        self.link_post_to_tags(post_id, new_tags_ids)

    def get_or_create_tag(self, slug: str, type: str):
        current = (
            self.supabase.from_("tags")
            .select("*")
            .eq("type", type)
            .eq("slug", slug)
            .execute()
        )

        if len(current.data) > 0:
            # exists
            return current.data[0]["id"]
        else:
            # add
            bbb = (
                self.supabase.from_("tags")
                .insert(
                    {
                        "type": type,
                        "slug": slug,
                        "name": slug,
                    }
                )
                .execute()
            )
            return bbb.data[0]["id"]

    def link_post_to_tags(self, post_id, tags_ids):
        for tag_id in tags_ids:
            self.supabase.from_("posts_tags").insert(
                {
                    "post_id": post_id,
                    "tag_id": tag_id,
                }
            ).execute()
