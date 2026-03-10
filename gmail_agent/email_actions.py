from googleapiclient.discovery import build

import base64

def reply_email(creds, gmail_id, reply_text):
    service = build("gmail", "v1", credentials=creds)

    # Get original message to fetch headers
    message = service.users().messages().get(
        userId="me",
        id=gmail_id,
        format="metadata",
        metadataHeaders=["Subject", "From"]
    ).execute()

    headers = message.get("payload", {}).get("headers", [])
    subject = ""
    sender = ""

    for h in headers:
        if h["name"] == "Subject":
            subject = h["value"]
        elif h["name"] == "From":
            raw_sender = h["value"]

            if "<" in raw_sender:
                sender = raw_sender.split("<")[1].replace(">", "").strip()
            else:
                sender = raw_sender.strip()

    raw_message = f"To: {sender}\r\nSubject: Re: {subject}\r\n\r\n{reply_text}"

    encoded_message = base64.urlsafe_b64encode(
        raw_message.encode("utf-8")
    ).decode("utf-8")

    service.users().messages().send(
        userId="me",
        body={"raw": encoded_message}
    ).execute()

    return "Reply has been sent."


def delete_email(creds, gmail_id):
    """
    Move an email to trash.
    """
    service = build("gmail", "v1", credentials=creds)

    service.users().messages().trash(
        userId="me",
        id=gmail_id
    ).execute()

    return "The email has been moved to trash."
def get_or_create_label(creds, label_name):

    # normalize label name
    label_name = label_name.lower().strip()

    service = build("gmail", "v1", credentials=creds)

    labels = service.users().labels().list(userId="me").execute()

    for label in labels.get("labels", []):
        if label["name"].lower() == label_name:
            return label["id"]

    new_label = service.users().labels().create(
        userId="me",
        body={
            "name": label_name,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show"
        }
    ).execute()

    return new_label["id"]


def add_label_to_email(creds, message_id, label_id):

    service = build("gmail", "v1", credentials=creds)

    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={
            "addLabelIds": [label_id],
            "removeLabelIds": []
        }
    ).execute()