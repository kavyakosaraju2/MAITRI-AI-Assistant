import base64
import re
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

def clean_email_text(raw_html):
    if not raw_html:
        return ""

    soup = BeautifulSoup(raw_html, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def read_latest_emails(creds, max_results=10):
    service = build("gmail", "v1", credentials=creds)

    # 🔹 Always fetch newest INBOX emails
    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=max_results
    ).execute()

    messages = results.get("messages", [])
    emails = []

    if not messages:
        print("No emails found.")
        return []

    print("\n📧 Latest Emails:\n")

    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()

        headers = msg_data["payload"].get("headers", [])
        labels = msg_data.get("labelIds", [])

        # 🚫 Skip obvious noise
        if any(l in labels for l in ["CATEGORY_PROMOTIONS", "CATEGORY_SOCIAL", "CATEGORY_FORUMS"]):
            continue

        subject = "No Subject"
        sender = "Unknown"

        for h in headers:
            if h["name"] == "Subject":
                subject = h["value"]
            elif h["name"] == "From":
                sender = h["value"]

        body = ""
        payload = msg_data["payload"]

        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/html":
                    data = part["body"].get("data")
                    if data:
                        html = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                        body = clean_email_text(html)
                        break
        else:
            data = payload["body"].get("data")
            if data:
                html = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                body = clean_email_text(html)

        print(f"From: {sender}")
        print(f"Subject: {subject}")
        print("-" * 40)

        emails.append({
            "from": sender,
            "subject": subject,
            "body": body,
            "labels": labels
        })

        if len(emails) >= 5:
            break  # only latest 5 useful emails

    return emails



