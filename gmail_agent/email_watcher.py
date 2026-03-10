import time
from datetime import datetime

from gmail_agent.gmail_reader import read_latest_emails
from database.email_repository import email_exists, save_email_result
from agent_brain.email_summarizer import summarize_email
from agent_brain.context_memory import memory
from gmail_agent.gmail_labels import get_or_create_label, apply_label_to_email
from googleapiclient.discovery import build

def start_email_watcher(creds, user_id):

    print("📡 Email watcher started...")

    while True:

        emails = read_latest_emails(creds)

        for email in emails:

            gmail_id = email.get("id")

            already_exists = email_exists(gmail_id)

            subject = email.get("subject", "")
            sender = email.get("from", "")
            received_at = email.get("received_at", "")
            body = email.get("body", "")

            # -------------------------------------------------
            # LINKEDIN EMAIL AUTO LABEL
            # -------------------------------------------------
            if "linkedin" in sender.lower() or "linkedin" in subject.lower() or "linkedin" in body.lower():
                if already_exists:
                     continue

                try:

                    label_id = get_or_create_label(creds, "LinkedIn Updates")

                    apply_label_to_email(creds, gmail_id, label_id)

                    service = build("gmail", "v1", credentials=creds)

                    service.users().messages().modify(
                        userId="me",
                        id=gmail_id,
                        body={"removeLabelIds": ["INBOX"]}
                    ).execute()

                    #print("LinkedIn email moved:", subject)

                except Exception as e:
                    print("LinkedIn processing error:", e)

                continue
            received_at = email.get("received_at", "")
            body = email.get("body", "")
            #print("EMAIL BODY:", body[:200])

            result = summarize_email(body)

            summary = str(result[0]) if len(result) > 0 else ""
            meeting = result[1] if len(result) > 1 else None
            tasks = result[2] if len(result) > 2 else []
            #print("TASKS DETECTED:", tasks)
             
            if tasks:
              memory.last_extracted_tasks = tasks
        
            tokens = result[3] if len(result) > 3 else 0

            #print("Extracted meeting:", meeting)
           

            # -------------------------------------------------
            # FIX: Normalize AM/PM time if LLM returns early AM
            # -------------------------------------------------
            if meeting and "datetime" in meeting:

                try:
                    dt = datetime.strptime(meeting["datetime"], "%Y-%m-%d %H:%M")

                    # If time is early morning (likely meant PM)
                    if dt.hour < 8:
                        dt = dt.replace(hour=dt.hour + 12)

                    meeting["datetime"] = dt.strftime("%Y-%m-%d %H:%M")

                except Exception as e:
                    print("⚠ Time normalization failed:", e)

            # Store meeting in memory so assistant can ask user
            if meeting:
                #print("Meeting detected from email:", meeting)
                memory.last_meeting = meeting

            # Ensure tokens is a valid integer
            try:
                tokens = int(tokens)
            except:
                tokens = 0

            #print("Saved email:", subject)

            if not already_exists:

                save_email_result(
                    user_id,
                    gmail_id,
                    subject,
                    sender,
                    received_at,
                    summary,
                    meeting,
                    tasks,
                    tokens
                )

        time.sleep(5)