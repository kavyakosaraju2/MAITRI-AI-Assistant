import base64
import re
from googleapiclient.discovery import build
from bs4 import BeautifulSoup


# -------------------------------------------------
# CLEAN HTML EMAIL TEXT
# -------------------------------------------------
def clean_email_text(raw_html):

    if not raw_html:
        return ""

    soup = BeautifulSoup(raw_html, "html.parser")

    # Remove scripts and styles
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator=" ")

    text = re.sub(r"\s+", " ", text).strip()

    return text


# -------------------------------------------------
# RECURSIVE EMAIL BODY EXTRACTOR
# -------------------------------------------------
def extract_body(payload):

    bodies = []

    # Collect all possible bodies
    if "parts" in payload:
        for part in payload["parts"]:
            body = extract_body(part)
            if body:
                bodies.append(body)

    mime_type = payload.get("mimeType", "")

    if mime_type == "text/plain":
        data = payload.get("body", {}).get("data")
        if data:
            bodies.append(
                base64.urlsafe_b64decode(data).decode(
                    "utf-8", errors="ignore"
                )
            )

    if mime_type == "text/html":
        data = payload.get("body", {}).get("data")
        if data:
            html = base64.urlsafe_b64decode(data).decode(
                "utf-8", errors="ignore"
            )
            bodies.append(clean_email_text(html))

    # Return the longest body
    if bodies:
        return max(bodies, key=len)

    return ""

# -------------------------------------------------
# READ LATEST EMAILS
# -------------------------------------------------
def read_latest_emails(creds, max_results=15):

    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=max_results
    ).execute()

    messages = results.get("messages", [])

    if not messages:
        return []

    emails = []

    for msg in messages:

        try:

            msg_data = service.users().messages().get(
                userId="me",
                id=msg["id"],
                format="full"
            ).execute()

            internal_date = int(msg_data.get("internalDate", 0))

        except Exception as e:
            print("⚠ Skipping email due to API error:", e)
            continue

        payload = msg_data.get("payload", {})
        headers = payload.get("headers", [])
        labels = msg_data.get("labelIds", [])

        # Skip noisy categories
        # Skip noisy categories but allow LinkedIn emails
        if "CATEGORY_PROMOTIONS" in labels or "CATEGORY_FORUMS" in labels:
            continue

        subject = "No Subject"
        sender = "Unknown"
        date = None

        for h in headers:

            if h["name"] == "Subject":
                subject = h["value"]

            elif h["name"] == "From":

                raw_sender = h["value"]

                if "<" in raw_sender:
                    sender = raw_sender.split("<")[0].strip().replace('"', "")
                else:
                    sender = raw_sender.strip()

            elif h["name"] == "Date":
                date = h["value"]

        # Extract body safely
        body = extract_body(payload)

        emails.append({
            "id": msg["id"],
            "from": sender,
            "subject": subject,
            "body": body,
            "labels": labels,
            "received_at": date,
            "internal_date": internal_date
        })

    # Sort newest first
    emails = sorted(
        emails,
        key=lambda x: x["internal_date"],
        reverse=True
    )

    return emails