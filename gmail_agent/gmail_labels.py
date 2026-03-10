from googleapiclient.discovery import build


def get_or_create_label(creds, label_name):

    service = build("gmail", "v1", credentials=creds)

    labels = service.users().labels().list(userId="me").execute()

    for label in labels.get("labels", []):
        if label["name"].lower() == label_name.lower():
            return label["id"]

    label_object = {
        "name": label_name,
        "labelListVisibility": "labelShow",
        "messageListVisibility": "show"
    }

    created_label = service.users().labels().create(
        userId="me",
        body=label_object
    ).execute()

    return created_label["id"]


def apply_label_to_email(creds, gmail_id, label_id):

    service = build("gmail", "v1", credentials=creds)

    service.users().messages().modify(
        userId="me",
        id=gmail_id,
        body={"addLabelIds": [label_id]}
    ).execute()