from googleapiclient.discovery import build


def move_to_spam(creds, gmail_id):

    print(f"Moving email {gmail_id} to spam...")

    service = build("gmail", "v1", credentials=creds)

    service.users().messages().modify(
        userId="me",
        id=gmail_id,
        body={
            "addLabelIds": ["SPAM"],
            "removeLabelIds": [
                "INBOX",
                "CATEGORY_PERSONAL",
                "CATEGORY_UPDATES",
                "CATEGORY_SOCIAL",
                "CATEGORY_PROMOTIONS"
            ]
        }
    ).execute()

    return "Email moved to spam."