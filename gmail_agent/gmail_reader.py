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

    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=max_results
    ).execute()

    messages = results.get("messages", [])
    emails = []

    if not messages:
        return []

    for msg in messages:

        msg_data = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()

        headers = msg_data["payload"].get("headers", [])
        labels = msg_data.get("labelIds", [])

        # Skip noise categories
        if any(l in labels for l in [
            "CATEGORY_PROMOTIONS",
            "CATEGORY_SOCIAL",
            "CATEGORY_FORUMS"
        ]):
            continue

        subject = "No Subject"
        sender = "Unknown"
        date = None  # 🔹 NEW: Extract date

        for h in headers:
            if h["name"] == "Subject":
                subject = h["value"]
            elif h["name"] == "From":
                sender = h["value"]
            elif h["name"] == "Date":
                date = h["value"]  # 🔹 Save raw email date

        body = ""
        payload = msg_data["payload"]

        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/html":
                    data = part["body"].get("data")
                    if data:
                        html = base64.urlsafe_b64decode(data).decode(
                            "utf-8", errors="ignore"
                        )
                        body = clean_email_text(html)
                        break
        else:
            data = payload["body"].get("data")
            if data:
                html = base64.urlsafe_b64decode(data).decode(
                    "utf-8", errors="ignore"
                )
                body = clean_email_text(html)

        emails.append({
            "from": sender,
            "subject": subject,
            "body": body,
            "labels": labels,
            "date": date  # 🔹 NEW FIELD ADDED
        })

        if len(emails) >= 5:
            break

    return emails
