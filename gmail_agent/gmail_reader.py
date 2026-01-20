from googleapiclient.discovery import build
import base64

def read_latest_emails(creds, max_results=5):
    gmail_service = build("gmail", "v1", credentials=creds)

    results = gmail_service.users().messages().list(
        userId="me",
        maxResults=max_results
    ).execute()

    messages = results.get("messages", [])

    if not messages:
        print("No emails found.")
        return []

    email_data = []
    print("\n📧 Latest Emails:\n")

    for msg in messages:
        msg_data = gmail_service.users().messages().get(
            userId="me",
            id=msg["id"]
        ).execute()

        headers = msg_data["payload"]["headers"]
        parts = msg_data["payload"].get("parts", [])
        body = ""

        # Extract plain text body
        for part in parts:
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data")
                if data:
                    body = base64.urlsafe_b64decode(
                        data
                    ).decode("utf-8", errors="ignore")

        subject = "No Subject"
        sender = "Unknown"

        for header in headers:
            if header["name"] == "Subject":
                subject = header["value"]
            if header["name"] == "From":
                sender = header["value"]

        print(f"From: {sender}")
        print(f"Subject: {subject}")

        email_data.append({
            "from": sender,
            "subject": subject,
            "body": body
        })

        print("-" * 40)

    return email_data
