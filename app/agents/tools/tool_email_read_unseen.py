import os
import imaplib

from email.parser import BytesParser

from pydantic import BaseModel


class EmailReadUnseenResponse(BaseModel):
    from_address: str
    subject: str
    date: str


def tool_email_read_unseen() -> list[EmailReadUnseenResponse] | str:

    mail = imaplib.IMAP4_SSL(os.getenv("IMAP_SERVER_NAME"))

    mail.login(os.getenv("IMAP_USER"), os.getenv("IMAP_PASSWORD"))

    mail.select("INBOX")

    status, data = mail.search(None, "UNSEEN")

    if status != "OK":
        return "SEARCH_FAILED"

    if data[0] is None:
        return "NO_EMAIL_FOUND"

    email_ids = data[0].split()

    email_reads_unseen_list: list[EmailReadUnseenResponse] = []

    for email_id in email_ids:
        email_str = email_id.decode("utf-8")
        status, msg_data = mail.fetch(email_str, "(BODY.PEEK[])")
        if status == "OK":
            email_bytes = msg_data[0][1]
            msg_obj = BytesParser().parsebytes(email_bytes)
            email_reads_unseen_list.append(
                EmailReadUnseenResponse(
                    from_address=msg_obj.get("From"),
                    subject=msg_obj.get("Subject"),
                    date=msg_obj.get("Date"),
                )
            )

    mail.logout()

    return email_reads_unseen_list
