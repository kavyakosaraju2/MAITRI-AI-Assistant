from agent_brain.email_summarizer import summarize_email
from auth.google_auth import google_login
from gmail_agent.gmail_reader import read_latest_emails
from calendar_agent.calendar_reader import read_upcoming_events
from task_agent.task_reader import read_tasks
from agent_brain.summary import generate_summary
from voice.voice_input import listen_to_user
from voice.voice_output import speak


print("MAITRI is starting...\n")

# -----------------------------
# GOOGLE LOGIN (ONLY ONCE)
# -----------------------------
creds = google_login()
print("🔐 Google login completed\n")

# -----------------------------
# READ DATA FROM GOOGLE
# -----------------------------
print("📧 GMAIL SUMMARY")
emails = read_latest_emails(creds)
print("\n🧠 AI EMAIL UNDERSTANDING\n")

if emails:
    first_email = emails[0]
    email_text = first_email.get("body", "")

    summary = summarize_email(email_text)

    print("📌 Email Summary:")
    print(summary)

    speak(summary)


print("\n📅 CALENDAR SUMMARY")
events = read_upcoming_events(creds)

print("\n📋 TASK SUMMARY")
tasks = read_tasks(creds)

# -----------------------------
# GENERATE TEXT SUMMARY
# -----------------------------
summary_text = generate_summary(emails, events, tasks)
speak(summary_text)


# -----------------------------
# VOICE OUTPUT (GREETING)
# -----------------------------
speak("Hello, I am MAITRI. I am ready to help you.")

# -----------------------------
# VOICE INPUT + ECHO
# -----------------------------
print("\n🎧 VOICE INPUT MODE")
user_command = listen_to_user()

if user_command:
    speak(f"You said {user_command}")

