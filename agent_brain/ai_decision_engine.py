import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from agent_brain.context_memory import memory
from database.email_repository import email_exists, get_email, save_email_result
from database.token_repository import log_token_usage

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------------------------------
# INTENT CLASSIFIER
# -------------------------------------------------
def classify_intent(user_command):

    previous_query = memory.last_user_query or ""

    prompt = f"""
    You are an intent classifier for an email assistant.

    Previous user message:
    {previous_query}

    Current user message:
    {user_command}

    Classify into one of:

    - MULTI_EMAIL (referring to multiple emails or comparing)
    - SINGLE_EMAIL (referring to one specific email)
    - EMAIL_OVERVIEW (asking about inbox status, unread count, latest email, urgent emails)
    - NON_EMAIL (unrelated to email)

    Respond ONLY in JSON:
    {{ "intent": "EMAIL_OVERVIEW" }}
    """

   

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=15
    )

    try:
        intent = json.loads(response.choices[0].message.content)["intent"]
    except:
        intent = "NON_EMAIL"

    memory.last_user_query = user_command
    memory.last_intent = intent

    print(f"🧭 Intent classified as: {intent}")
    return intent


# -------------------------------------------------
# FORMAT EMAILS
# -------------------------------------------------
def format_emails(emails):
    formatted = ""
    for i, email in enumerate(emails[:3]):
        formatted += f"""
Email {i+1}:
From: {email.get('from')}
Subject: {email.get('subject')}
Date: {email.get('date')}
Body: {email.get('body')[:250]}
"""
    return formatted


# -------------------------------------------------
# SYSTEM PROMPT
# -------------------------------------------------
SYSTEM_PROMPT = """
You are MAITRI.

When analyzing a single email, respond ONLY in JSON:

{
  "reply": "...",
  "meeting": {
      "title": "...",
      "datetime": "YYYY-MM-DD HH:MM"
  } or null,
  "tasks": [
      {"title": "...", "due": "YYYY-MM-DD"}
  ] or []
}
"""


# -------------------------------------------------
# MAIN DECISION ENGINE
# -------------------------------------------------
def ai_decision_engine(user_command, emails, events, tasks):

    print("🧠 Thinking...")
    print("DEBUG: Emails received:", len(emails))

    user_command = user_command.strip()
    lower = user_command.lower()

    # =====================================================
    # 1️⃣ HANDLE CONFIRMATION
    # =====================================================
    if memory.pending_action:

        if "yes" in lower:
            action = memory.pending_action
            memory.pending_action = None

            from calendar_agent.calendar_reader import create_calendar_event
            from task_agent.task_reader import create_task

            if action.get("meeting"):
                create_calendar_event(
                    action["creds"],
                    action["meeting"]["title"],
                    action["meeting"]["datetime"]
                )

            for t in action.get("tasks", []):
                create_task(
                    action["creds"],
                    t.get("title"),
                    t.get("due")
                )

            return "Meeting and tasks added successfully."

        if "no" in lower:
            memory.pending_action = None
            return "Okay, I will not add them."

    # =====================================================
    # 2️⃣ DEFINE EMAIL CONTEXT FIRST (CRITICAL)
    # =====================================================
    latest_email = emails[0] if emails else None
    recent_emails = emails[:5] if emails else []
    gmail_id = latest_email.get("id") if latest_email else None

    # =====================================================
    # 3️⃣ CONTEXT-AWARE INTENT CLASSIFICATION
    # =====================================================
    if any(word in lower for word in ["this", "it", "that"]):
        if memory.last_context_type in ["SINGLE_EMAIL", "MULTI_EMAIL"]:
            intent = memory.last_context_type
            print(f"🧠 Using previous context: {intent}")
        else:
            intent = classify_intent(user_command)
    else:
        intent = classify_intent(user_command)

    memory.last_context_type = intent

    if intent == "EMAIL_OVERVIEW":

        unread_count = sum(
            1 for e in emails if "UNREAD" in e.get("labels", [])
        )

        if "unread" in lower:
            return f"You have {unread_count} unread emails."

        if "latest" in lower:
            if latest_email:
                return f"The latest email is from {latest_email.get('from')} with subject '{latest_email.get('subject')}'."
            else:
                return "You have no emails."

        return "You have emails in your inbox."

    # =====================================================
    # 4️⃣ MULTI EMAIL REASONING
    # =====================================================
    if intent == "MULTI_EMAIL" and recent_emails:

        email_context = format_emails(recent_emails)

        prompt = f"""
Here are recent emails:

{email_context}

User question:
{user_command}

Answer clearly and directly.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )

        print(f"🔢 Multi-email Tokens: {response.usage.total_tokens}")
        return response.choices[0].message.content

    # =====================================================
    # 5️⃣ SINGLE EMAIL CACHE REASONING
    # =====================================================
    if intent == "SINGLE_EMAIL" and latest_email and gmail_id:

        if email_exists(gmail_id):

            cached = get_email(gmail_id)
            print("⚡ Using cached email data")

            reasoning_prompt = f"""
Stored Email Data:

Summary:
{cached.get("summary")}

Meeting:
{cached.get("meeting")}

Tasks:
{cached.get("tasks")}

User question:
{user_command}

Answer using ONLY stored data.
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": reasoning_prompt}],
                max_tokens=150
            )

            print(f"🔢 Reasoning Tokens: {response.usage.total_tokens}")
            return response.choices[0].message.content

    # =====================================================
    # 6️⃣ FIRST TIME SINGLE EMAIL PROCESSING
    # =====================================================
    if intent == "SINGLE_EMAIL" and latest_email:

        email_context = format_emails([latest_email])

        prompt = f"""
Latest email:

{email_context}

User question:
{user_command}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )

        print(f"🔢 Tokens used: {response.usage.total_tokens}")

        try:
            data = json.loads(response.choices[0].message.content)
        except:
            return response.choices[0].message.content

        reply = data.get("reply")
        meeting = data.get("meeting")
        extracted_tasks = data.get("tasks", [])

        if gmail_id and not email_exists(gmail_id):

            save_email_result(
                user_id=os.getenv("USER_ID"),
                gmail_id=gmail_id,
                subject=latest_email.get("subject"),
                sender=latest_email.get("from"),
                received_at=latest_email.get("date"),
                summary=reply,
                meeting=meeting,
                tasks=extracted_tasks,
                tokens_used=response.usage.total_tokens
            )

            log_token_usage(
                os.getenv("USER_ID"),
                gmail_id,
                response.usage.total_tokens
            )

        if (meeting or extracted_tasks) and gmail_id and not email_exists(gmail_id):

            memory.pending_action = {
                "meeting": meeting,
                "tasks": extracted_tasks,
                "creds": memory.creds
            }

            message = reply + "\n\nI detected:\n"

            if meeting:
                message += f"- Meeting on {meeting['datetime']}\n"

            if extracted_tasks:
                message += f"- {len(extracted_tasks)} task(s)\n"

            message += "\nShould I add them?"

            return message

        return reply

    # =====================================================
    # 7️⃣ NON EMAIL REQUEST
    # =====================================================
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_command}],
        max_tokens=120
    )

    print(f"🔢 General Tokens: {response.usage.total_tokens}")
    return response.choices[0].message.content