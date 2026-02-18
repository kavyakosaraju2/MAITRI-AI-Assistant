from agent_brain.email_summarizer import summarize_email
from agent_brain.summary import generate_summary
from agent_brain.question_answering import answer_question
from agent_brain.decision_engine import decide_response   # ✅ NEW

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

from agent_brain.context_memory import memory
memory.creds = creds

# -------------------------------------------------
# VOICE COMMAND MODE – PHASE 15 (AI BASED)
# -------------------------------------------------
from agent_brain.context_memory import memory

startup_message = "Hello! I am ready to help you."
print(startup_message)
speak(startup_message)

print("\n🎧 VOICE COMMAND MODE (say 'stop' to exit)")

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

    response = decide_response(user_command, emails, events, tasks)

    if not response:
        response = "I am not sure how to respond to that."

    print("\n🧠 RESPONSE:", response)
    speak(response)


