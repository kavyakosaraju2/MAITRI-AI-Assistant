import time
from gmail_agent.gmail_reader import read_latest_emails

seen_email_ids = set()

def start_live_email_monitor(creds, interval=30):
    print("📡 MAITRI Live Email Monitoring Started...\n")

    global seen_email_ids

    while True:
        try:
            emails = read_latest_emails(creds)

            for email in emails:
                if email["id"] not in seen_email_ids:
                    seen_email_ids.add(email["id"])

                    print("\n📩 New Email Detected")
                    print("From:", email["from"])
                    print("Subject:", email["subject"])
                    print("Date:", email["date"])

            time.sleep(interval)

        except Exception as e:
            print("❌ Error checking emails:", e)
            time.sleep(interval)