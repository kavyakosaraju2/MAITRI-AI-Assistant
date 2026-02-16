from agent_brain.command_processor import process_command
from agent_brain.email_summarizer import summarize_email
from agent_brain.summary import generate_summary
from agent_brain.question_answering import answer_question

from auth.google_auth import google_login
from gmail_agent.gmail_reader import read_latest_emails
from calendar_agent.calendar_reader import read_upcoming_events
from task_agent.task_reader import read_tasks

from voice.voice_input import listen_to_user
from voice.voice_output import speak


print("MAITRI is starting...\n")

# -------------------------------------------------
# GOOGLE LOGIN (ONLY ONCE)
# -------------------------------------------------
creds = google_login()
print("🔐 Google login completed\n")

# -------------------------------------------------
# INITIAL DATA FETCH (ON START)
# -------------------------------------------------
print("📧 Fetching emails...")
emails = read_latest_emails(creds)

print("\n📅 Fetching calendar events...")
events = read_upcoming_events(creds)

print("\n📋 Fetching tasks...")
tasks = read_tasks(creds)

# -------------------------------------------------
# AI EMAIL UNDERSTANDING (FIRST EMAIL ONLY)
# -------------------------------------------------
if emails:
    print("\n🧠 AI EMAIL UNDERSTANDING\n")

    first_email = emails[0]
    email_text = first_email.get("body", "")

    email_summary = summarize_email(email_text)

    print("📌 Email Summary:")
    print(email_summary)
    speak(email_summary)

# -------------------------------------------------
# DAILY SUMMARY (TEXT + VOICE)
# -------------------------------------------------
daily_summary = generate_summary(emails, events, tasks)

print("\n🧠 DAILY SUMMARY\n")
print(daily_summary)
speak(daily_summary)

# -------------------------------------------------
# VOICE COMMAND MODE (PHASE 13 – FIXED)
# -------------------------------------------------
speak("Hello, I am MAITRI. I am ready to help you.")
print("\n🎧 VOICE COMMAND MODE (say 'stop' to exit)")

while True:
    user_command = listen_to_user()

    if not user_command:
        speak("I did not understand. Please try again.")
        continue

    action = process_command(user_command)

    # ---------------- COMMAND HANDLING ----------------

    if action == "READ_EMAILS":
        speak("Reading your latest emails")
        read_latest_emails(creds)
        continue

    elif action == "READ_CALENDAR":
        speak("Here are your upcoming calendar events")
        read_upcoming_events(creds)
        continue

    elif action == "READ_TASKS":
        speak("Here are your pending tasks")
        read_tasks(creds)
        continue

    elif action == "READ_SUMMARY":
        speak("Here is your daily summary")
        daily_summary = generate_summary(emails, events, tasks)
        speak(daily_summary)
        continue

   
    elif action == "CHECK_TASKS":
        pending = [t for t in tasks if t["status"] == "needsAction"]
        if pending:
            response = f"You have {len(pending)} pending tasks."
            for t in pending:
                response += f" {t['title']} due on {t.get('due', 'no deadline')}."
        else:
            response = "You have no pending tasks."
        print("🧠 ANSWER:", response)
        speak(response)
        continue


    elif action == "STOP":
        speak("Okay. I am stopping now.")
        print("🛑 MAITRI stopped.")
        break

    # ---------------- AI QUESTION ANSWERING ----------------
    else:
        answer = answer_question(user_command, emails)
        print("🧠 ANSWER:", answer)
        speak(answer)
        continue


