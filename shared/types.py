class EmailMessage:
    def __init__(self, from_email, to_email, subject, date, message_id, body):
        self.body = body
        self.from_email = from_email
        self.to_email = to_email
        self.subject = subject
        self.date = date
        self.message_id = message_id


class PostMessage:
    def __init__(self, email_id, url, title, text, domains, categories, tags, new_tags):
        self.email_id = email_id
        self.url = url
        self.title = title
        self.text = text
        self.domains = domains
        self.categories = categories
        self.tags = tags
        self.new_tags = new_tags
