from imapclient import IMAPClient
import email
from email.policy import default
import os

# https://imapclient.readthedocs.io/en/3.0.0/


class EmailMessage:
    def __init__(self, from_email, to_email, subject, date, message_id, body):
        self.body = body
        self.from_email = from_email
        self.to_email = to_email
        self.subject = subject
        self.date = date
        self.message_id = message_id


class EmailService:
    def __init__(
        self, imap_host: str, imap_port: int, imap_user: str, imap_password: str
    ):
        self.__imap_host = imap_host
        self.__imap_port = imap_port
        self.__imap_user = imap_user
        self.__imap_password = imap_password

        self.__server = IMAPClient(imap_host, port=imap_port, use_uid=True)
        self.__server.login(imap_user, imap_password)

    def fetch_unseen_mails(self, folder_name, from_filter=None):
        self.__server.select_folder(folder_name)

        if from_filter:
            messages_ids = self.__server.search(["UNSEEN", "FROM", from_filter])
        else:
            messages_ids = self.__server.search(["UNSEEN"])

        return messages_ids

    def fetch_message(self, message_id, folder_name):
        self.__server.select_folder(folder_name)

        message_id_int = int(message_id)
        messages_data = self.__server.fetch(message_id_int, ["RFC822"])
        message_data = messages_data[message_id_int]

        email_message = email.message_from_bytes(
            message_data[b"RFC822"], policy=default
        )

        html_content = ""
        if not email_message.is_multipart():
            html_content = email_message.get_payload(decode=True).decode("utf-8")
        else:
            for part in email_message.walk():
                if part.get_content_type() == "text/html":
                    html_content = part.get_payload(decode=True).decode("utf-8")
                    break

        return EmailMessage(
            from_email=email_message.get("From"),
            to_email=email_message.get("To"),
            subject=email_message.get("Subject"),
            date=email_message.get("Date"),
            message_id=email_message.get("Message-Id"),
            body=html_content,
        )

    def mark_massage_as_seen(self, message_id, folder_name):
        self.__server.select_folder(folder_name)
        self.__server.add_flags(message_id, [b"\\Seen"])

    def mark_massage_as_unseen(self, message_id, folder_name):
        self.__server.select_folder(folder_name)
        self.__server.remove_flags(message_id, [b"\\Seen"])
