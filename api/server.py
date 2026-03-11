from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Kavya backend modules
from agent_brain.command_processor import process_command
from voice.voice_input import listen_to_user

app = FastAPI()

# Allow Flutter app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===============================
# COMMAND (Assistant interaction)
# ===============================

@app.post("/command")
def command(data: dict):

    user_command = data["command"]

    # Voice input
    if user_command == "listen":

        user_command = listen_to_user()

        if not user_command:
            return {
                "command": "",
                "response": "Sorry, I didn't catch that. Please repeat."
            }

    response = process_command(user_command)

    return {
        "command": user_command,
        "response": response
    }


# ===============================
# DASHBOARD STATUS
# ===============================

@app.get("/status")
def get_status():

    from gmail_agent.gmail_reader import read_latest_emails
    from calendar_agent.calendar_reader import read_upcoming_events
    from task_agent.task_reader import read_tasks
    from auth.google_auth import google_login

    creds = google_login()


    emails = read_latest_emails(creds)
    events = read_upcoming_events(creds)
    tasks = read_tasks(creds)

    return {
        "emails": [e.get("subject", "") for e in emails],
        "events": [e.get("summary", "") for e in events],
        "tasks": [t.get("title", "") for t in tasks]
    }


# ===============================
# CHAT HISTORY
# ===============================

@app.get("/chats")
def get_chats():

    from database.db_client import get_chats

    return get_chats()


@app.post("/save_chat")
def save_chat(data: dict):

    from database.db_client import save_chat

    title = data["title"]
    messages = data["messages"]
    chat_id = data.get("chat_id")

    chat_id = save_chat(title, messages, chat_id)

    return {"chat_id": chat_id}


@app.delete("/delete_chat/{chat_id}")
def delete_chat(chat_id: str):

    from database.db_client import delete_chat

    delete_chat(chat_id)

    return {"status": "deleted"}


# ===============================
# EMAILS
# ===============================

@app.get("/emails")
def emails():

    from gmail_agent.gmail_reader import read_latest_emails
    from auth.google_auth import google_login

    creds = google_login()

    return read_latest_emails(creds)


# ===============================
# CALENDAR
# ===============================

@app.get("/calendar")
def calendar():

    from auth.google_auth import google_login
    from calendar_agent.calendar_reader import read_upcoming_events

    creds = google_login()

    events = read_upcoming_events(creds)

    formatted_events = []

    for e in events:

        title = e.get("summary", "No Title")

        start = e.get("start", {})

        if "dateTime" in start:
            time = start["dateTime"]
        elif "date" in start:
            time = start["date"]
        else:
            time = "No time"

        formatted_events.append({
            "title": title,
            "time": time
        })

    return formatted_events


# ===============================
# TASKS
# ===============================

@app.get("/tasks")
def tasks():

    from auth.google_auth import google_login
    from task_agent.task_reader import read_tasks

    creds = google_login()

    tasks = read_tasks(creds)

    formatted_tasks = []

    for t in tasks:

        title = t.get("title", "Untitled task")

        formatted_tasks.append({
            "title": title
        })

    return formatted_tasks