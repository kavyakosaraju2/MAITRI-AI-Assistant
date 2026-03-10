# ENGINE TOGGLE
USE_AI_ENGINE = True   #  Change to False to use old decision_engine
from auth.google_auth import google_login
from gmail_agent.gmail_reader import read_latest_emails
from calendar_agent.calendar_reader import read_upcoming_events
from task_agent.task_reader import read_tasks

from voice.voice_input import listen_to_user
from voice.voice_output import speak
import threading
from gmail_agent.email_watcher import start_email_watcher

from agent_brain.context_memory import memory

if USE_AI_ENGINE:
    from agent_brain.ai_decision_engine import ai_decision_engine
else:
    from agent_brain.decision_engine import decide_response

# STARTUP
print("MAITRI is starting...\n")

# GOOGLE LOGIN (ONLY ONCE)
creds = google_login()
print("🔐 Google login completed\n")

memory.creds = creds

user_id = "969853fc-a331-4a27-a15d-23d520e8f313"

memory.user_id = user_id

threading.Thread(
    target=start_email_watcher,
    args=(creds, user_id),
    daemon=True
).start()

# GREETING

startup_message = "Hello! I am ready to help you."
print(startup_message)
speak(startup_message)

print("\n🎧 VOICE COMMAND MODE (say 'stop' to exit)")

# MAIN LOOP
while True:

    user_command = listen_to_user()

    if not user_command:
        speak("I did not understand. Please try again.")
        continue

    if user_command.lower() == "stop":
        speak("Okay. I am stopping now.")
        print("🛑 MAITRI stopped.")
        break

    # LIVE FETCH EVERY TIME
    emails = read_latest_emails(creds)
    events = read_upcoming_events(creds)
    tasks = read_tasks(creds)

    memory.creds = creds
    
    

    # Filter primary emails (remove promotions and social)
    filtered_emails = []

    for email in emails:
        labels = email.get("labels", [])

        if "CATEGORY_PROMOTIONS" not in labels and "CATEGORY_SOCIAL" not in labels:
            filtered_emails.append(email)

    emails = filtered_emails
    # DECISION ENGINE
    
    if USE_AI_ENGINE:
        response = ai_decision_engine(user_command, emails, events, tasks)

        # If AI returns JSON action
        if isinstance(response, dict):
            action = response.get("action")
            parameters = response.get("parameters", {})

            # ---- HANDLE ACTIONS ----
            if action == "read_emails":
                response = "You have {} recent emails.".format(len(emails))

            elif action == "daily_summary":
                response = f"You have {len(emails)} emails, {len(events)} events, and {len(tasks)} tasks."

            else:
                response = "I detected an action, but execution logic is not connected yet."

    else:
        response = decide_response(user_command, emails, events, tasks)

    # FALLBACK
    if not response:
        response = "I am not sure how to respond to that."

    print("\n🧠 RESPONSE:", response)
    speak(response)


