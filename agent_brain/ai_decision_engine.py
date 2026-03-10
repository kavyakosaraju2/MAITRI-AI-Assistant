import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

from agent_brain.context_memory import memory
from agent_brain.entity_extractor import extract_entities
from database.email_repository import email_exists, get_email, save_email_result
from database.token_repository import log_token_usage
from agent_brain.rag_engine import answer_email_question
from agent_brain.reply_generator import generate_reply
from calendar_agent.conflict_detector import check_calendar_conflict
from calendar_agent.calendar_actions import create_calendar_event
from calendar_agent.calendar_reader import read_upcoming_events
from agent_brain.rag_engine import categorize_emails_by_topic
from agent_brain.spam_detector import detect_spam_emails
from gmail_agent.email_actions import get_or_create_label, add_label_to_email
from gmail_agent.spam_actions import move_to_spam
from calendar_agent.calendar_reader import (
    read_upcoming_events,
    delete_calendar_event,
    find_event_for_deletion,
    update_calendar_event,
    rename_calendar_event
)

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

- MULTI_EMAIL
- SINGLE_EMAIL
- EMAIL_OVERVIEW
- NON_EMAIL

Respond ONLY in JSON:
{{ "intent": "EMAIL_OVERVIEW" }}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "You are a strict intent classifier. Always return valid JSON exactly as instructed."
            },
            {"role": "user", "content": prompt}
        ],
        max_tokens=40
    )

    print("RAW INTENT RESPONSE:", response.choices[0].message.content)

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

print("Memory last meeting:", memory.last_meeting)


def ai_decision_engine(user_command, emails, events, tasks):

    user_command = user_command.strip()
    lower = user_command.lower()
    # -------------------------------------------------
    # FOLLOW-UP: GROUPED EMAILS
    # -------------------------------------------------
    if "did you group" in lower or "show grouped emails" in lower or "show them" in lower:

        if memory.last_email_category:

            return "Yes, I grouped the emails related to your previous request."

        return "I haven't grouped any emails yet."
    # -------------------------------------------------
    # EMAIL REPLY CONFIRMATION
    # -------------------------------------------------
    if getattr(memory, "pending_reply", None):

        if any(word in lower for word in ["yes", "send", "go ahead", "send it"]):

            from gmail_agent.email_actions import reply_email

            reply = memory.pending_reply
            memory.pending_reply = None

            reply_email(
                memory.creds,
                reply["gmail_id"],
                reply["reply_text"]
            )

            return "✅ The reply has been sent."

        if any(word in lower for word in ["no", "cancel", "don't send"]):

            memory.pending_reply = None
            return "Okay, I will not send the reply."
    # -------------------------------------------------
    # 1️⃣ CONFIRMATION HANDLING
    # -------------------------------------------------
    if memory.pending_action:

        if "yes" in lower:

            action = memory.pending_action
            memory.pending_action = None

            if action["type"] == "create_event":
                return create_calendar_event(
                    memory.creds,
                    action["title"],
                    action["time"]
                )

            if action["type"] == "delete_event":
                delete_calendar_event(memory.creds, action["event_id"])
                return f"The meeting '{action['title']}' has been deleted."
            if action["type"] == "update_event":

                update_calendar_event(
                    memory.creds,
                    action["event_id"],
                    action["time"]
                )

                return f"The meeting '{action['title']}' has been rescheduled."
            if action["type"] == "rename_event":
                from calendar_agent.calendar_reader import rename_calendar_event

                rename_calendar_event(memory.creds, action["event_id"], action["title"])

                return f"The meeting has been renamed to '{action['title']}'."
            if action["type"] == "group_emails":
                topic = action["topic"]
                emails = action["emails"]

                label_id = get_or_create_label(memory.creds, topic)

                for email in emails:
                    add_label_to_email(memory.creds, email["gmail_id"], label_id)

                return f"I grouped {len(emails)} emails under the '{topic}' label."

            if action["type"] == "spam_cleanup":

                for email in action["emails"]:

                    move_to_spam(memory.creds, email["id"])
                return "Spam emails moved to the spam folder."
            
            print("ACTION TYPE:", action["type"])

            if action["type"] == "create_tasks":

                from task_agent.task_actions import create_task, task_exists

                tasks = action["tasks"]

                new_tasks = []
                skipped_tasks = []

                for task in tasks:

                    if task_exists(memory.creds, task["title"]):
                        skipped_tasks.append(task["title"])
                    else:
                        create_task(
                            memory.creds,
                            task["title"],
                            task["due"]
                        )
                        new_tasks.append(task["title"])

                if not new_tasks:
                    return "These tasks are already in your task list."

                return f"{len(new_tasks)} tasks have been added to your task list."
            
        if "no" in lower:
            memory.pending_action = None
            return "Okay, I will not proceed with the action."
    # 2️⃣ DELETE MEETING
    # -------------------------------------------------
    if ("delete" in lower or "remove" in lower) and "meeting" in lower:

        event = find_event_for_deletion(events, user_command)

        if not event:
            return "I could not find the meeting you want to delete."

        memory.pending_action = {
            "type": "delete_event",
            "event_id": event["id"],
            "title": event.get("summary", "Meeting")
        }

        return f"Do you want me to delete the meeting '{event.get('summary')}'?"
    # -------------------------------------------------
    # RESCHEDULE MEETING
    # -------------------------------------------------

    if ("move" in lower or "reschedule" in lower or "change time" in lower) and "meeting" in lower:

        entities = extract_entities(user_command)

        new_time = entities.get("datetime")

        if not new_time:
            return "What time should I move the meeting to?"

        event = find_event_for_deletion(events, user_command)

        if not event:
            return "I could not find the meeting you want to reschedule."

        memory.pending_action = {
            "type": "update_event",
            "event_id": event["id"],
            "title": event.get("summary", "Meeting"),
            "time": new_time
        }

        return f"Do you want me to move the meeting '{event.get('summary')}' to {new_time}?"
        # -------------------------------------------------
    # RENAME MEETING
    # -------------------------------------------------
    if "rename" in lower:

        event = find_event_for_deletion(events, user_command)

        if not event:
            return "I could not find the meeting you want to rename."

        # extract new title
        if "to" in lower:
            new_title = user_command.lower().split("to")[-1].strip()
        elif "as" in lower:
            new_title = user_command.lower().split("as")[-1].strip()
        else:
            return "What should I rename the meeting to?"

        memory.pending_action = {
            "type": "rename_event",
            "event_id": event["id"],
            "title": new_title,
            "old_title": event.get("summary", "Meeting")
        }

        return f"Do you want me to rename '{event.get('summary', 'meeting')}' to '{new_title}'?"
    # -------------------------------------------------
    # 3️⃣ SCHEDULE MEETING
    # -------------------------------------------------
    if "schedule" in lower:

        if "yesterday" in lower:
            return "I cannot schedule meetings in the past."
        

        entities = extract_entities(user_command)

        proposed_time = entities.get("datetime")

        if not proposed_time:
            return "What time should I schedule the meeting?"

        from datetime import datetime, timezone

        try:
            meeting_time = datetime.fromisoformat(proposed_time.replace("Z", "+00:00"))

            if meeting_time.tzinfo is None:
                meeting_time = meeting_time.replace(tzinfo=timezone.utc)

        except ValueError:
            return "I couldn't understand the meeting time."

        current_time = datetime.now(timezone.utc)

        if meeting_time < current_time:
            return "I cannot schedule meetings in the past."

        events = read_upcoming_events(memory.creds)

        conflict = check_calendar_conflict(proposed_time, events)

        if conflict:
            return f"You already have a meeting called '{conflict.get('summary')}' around that time."

        memory.pending_action = {
            "type": "create_event",
            "title": "Meeting",
            "time": proposed_time
        }

        return "The time is free. Should I schedule the meeting?"

    # -------------------------------------------------
    # 4️⃣ EMAIL REPLY
    # -------------------------------------------------
    if "reply" in lower:

        from agent_brain.rag_engine import find_email_for_action

        email_result = find_email_for_action(user_command, memory.user_id)

        if email_result:

            gmail_id = email_result.get("gmail_id")

            user_instruction = user_command.lower().split("saying")[-1].strip()

            reply_text = generate_reply(
                email_result["summary"],
                email_result["sender"],
                user_instruction
            )

            if not reply_text:
                return "What should I include in the reply?"

            memory.pending_reply = {
                "gmail_id": gmail_id,
                "reply_text": reply_text
            }

            return f"I found the email '{email_result.get('subject')}'. Should I send this reply?"


    # -------------------------------------------------
    # 5️⃣ SPAM DETECTION
    # -------------------------------------------------
    if "spam" in lower:

        spam_emails = detect_spam_emails(emails)

        if not spam_emails:
            return "I did not detect any spam emails."

        memory.pending_action = {
            "type": "spam_cleanup",
            "emails": spam_emails
        }

        response = f"I detected {len(spam_emails)} possible spam emails:\n\n"

        for i, email in enumerate(spam_emails, 1):
            response += f"{i}. {email['subject']}\n"

        response += "\nShould I move them to the spam folder?"

        return response
    # -------------------------------------------------
    # DIRECT LATEST EMAIL QUERY
    # -------------------------------------------------
    if "latest email" in lower or "most recent email" in lower:

        if emails:
            latest = emails[0]

            memory.last_email = latest  # ⭐ store context
            memory.last_context_type = "SINGLE_EMAIL" 

            subject = latest.get("subject", "No Subject")
            sender = latest.get("from", "Unknown Sender")

            return f"📧 Latest Email\nFrom: {sender}\nSubject: {subject}"

        return "You have no emails."
        # -------------------------------------------------
    # SUMMARIZE LATEST EMAIL
    # -------------------------------------------------
    if "summarize" in lower:

        if emails:
            latest = getattr(memory, "last_email", None) or (emails[0] if emails else None)

            prompt = f"""
    Summarize this email clearly in 2–3 sentences.

    From: {latest.get("from")}
    Subject: {latest.get("subject")}
    Body:
    {latest.get("body")}
    """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=120
            )

            return response.choices[0].message.content

        return "I could not find any email to summarize."
        # -------------------------------------------------
    # FOLLOW-UP QUESTIONS ABOUT LAST EMAIL
    # -------------------------------------------------
    if getattr(memory, "last_email", None):

        if "who sent" in lower or "who sent it" in lower:

            sender = memory.last_email.get("from", "Unknown Sender")
            return f"The email was sent by {sender}."

        if "what is the subject" in lower or "subject" in lower:

            subject = memory.last_email.get("subject", "No Subject")
            return f"The subject of the email is '{subject}'."

        if "when was it sent" in lower or "when did i receive it" in lower:

            date = memory.last_email.get("received_at", "Unknown date")
            return f"You received it on {date}."

        if "read it" in lower or "read the email" in lower:

            body = memory.last_email.get("body", "")
            return body[:500]
    
    # LIST RECENT EMAILS
    # -------------------------------------------------
    if "what emails" in lower or "emails did i receive" in lower or "show my emails" in lower:

        if not emails:
            return "You have not received any emails."

        response = "📨 Here are your recent emails:\n\n"

        for i, e in enumerate(emails[:5], 1):
            sender = e.get("from", "Unknown")
            subject = e.get("subject", "No Subject")

            response += f"{i}. {subject} — from {sender}\n"

        return response
        # -------------------------------------------------
    # WHO EMAILED RECENTLY
    # -------------------------------------------------
    if "who emailed" in lower or "who emailed me recently" in lower:

        if not emails:
            return "I couldn't find any recent emails."

        senders = []

        for e in emails[:5]:
            sender = e.get("from", "Unknown")
            if sender not in senders:
                senders.append(sender)

        response = "📧 Recently you received emails from:\n\n"

        for s in senders:
            response += f"- {s}\n"

        return response
    # -------------------------------------------------
    # MEETING DETECTION FROM EMAIL
    # -------------------------------------------------
    if "meeting" in lower and ("detect" in lower or "from my email" in lower):
        print("DEBUG MEMORY MEETING:", memory.last_meeting)

        from database.email_repository import get_email_meetings

        meetings = get_email_meetings(memory.user_id)

        if meetings:

            meeting = meetings[0]

            memory.last_meeting = meeting

            # ⭐ ADD THIS
            memory.pending_action = {
                "type": "create_event",
                "title": meeting["title"],
                "time": meeting["datetime"]
            }

            return f"I detected a meeting titled '{meeting['title']}' on {meeting['datetime']}. Should I schedule it on your calendar?"

        return "I did not detect any meeting invitations in your recent emails."
    # -------------------------------------------------
    # TASK DETECTION FROM EMAIL
    # -------------------------------------------------
    if "task" in lower or "tasks" in lower:

        tasks = getattr(memory, "last_extracted_tasks", [])

        if not tasks:
            return "I did not detect any tasks from your emails."

        response = "I detected these tasks from your email:\n\n"

        for i, task in enumerate(tasks, 1):
            response += f"{i}. {task['title']} — due {task['due']}\n"

        memory.pending_action = {
            "type": "create_tasks",
            "tasks": tasks
        }

        response += "\nShould I add them to your task list?"

        return response
   
    # -------------------------------------------------
    # 6️⃣ RAG QUERIES
    # -------------------------------------------------
    rag_triggers = [
        "email",
        "emails",
        "who emailed",
        "who sent",
        "did i receive",
        "did anyone send",
        "any email about",
        "email about",
        "emails about",
        "from ibm",
        "from deloitte",
        "from linkedin",
        "job email",
        "internship email"
    ]
    # -------------------------------------------------
    # GROUP EMAILS BY TOPIC (WITH CONFIRMATION)
    # -------------------------------------------------
    if "group" in lower and "email" in lower:

        topic = user_command.lower().split("related to")[-1].strip()

        grouped = categorize_emails_by_topic(topic, memory.user_id)

        if not grouped:
            return f"I couldn't find any emails related to {topic}."

        memory.pending_action = {
            "type": "group_emails",
            "emails": grouped,
            "topic": topic
        }

        preview = f"I found these emails related to {topic}:\n\n"

        for i, e in enumerate(grouped[:5], 1):
            preview += f"{i}. {e.get('subject')} — from {e.get('sender')}\n"

        preview += "\nShould I group these emails?"

        return preview
   

       
    # -------------------------------------------------
    # 6️⃣ RAG QUERIES
    # -------------------------------------------------
    if any(trigger in lower for trigger in rag_triggers):
        return answer_email_question(user_command, memory.user_id)

   

    print("🧠 Thinking...")
    print("DEBUG: Emails received:", len(emails))

    # -------------------------------------------------
    # EMAIL CONTEXT
    # -------------------------------------------------
    latest_email = None

    if emails:
        emails_sorted = sorted(
            emails,
            key=lambda e: e.get("internal_date", 0),
            reverse=True
        )

        latest_email = emails_sorted[0]

    recent_emails = emails[:5] if emails else []
    gmail_id = latest_email.get("id") if latest_email else None

    # -------------------------------------------------
    # INTENT CLASSIFICATION
    # -------------------------------------------------

    if any(word in lower for word in ["this", "it", "that", "them", "those"]):

        if memory.last_context_type in ["SINGLE_EMAIL", "MULTI_EMAIL", "EMAIL_OVERVIEW"]:

            intent = memory.last_context_type
            print(f"🧠 Using previous context: {intent}")
           

        else:

            intent = classify_intent(user_command)

    else:

        intent = classify_intent(user_command)

    memory.last_context_type = intent

    # -------------------------------------------------
    # EMAIL OVERVIEW
    # -------------------------------------------------

    if intent == "EMAIL_OVERVIEW":

        unread_count = sum(
            1 for e in emails if "UNREAD" in e.get("labels", [])
        )

        if "unread" in lower:
            return f"You have {unread_count} unread emails."

        if "latest" in lower:

            if latest_email:

                subject = latest_email.get("subject") or "No Subject"
                sender = latest_email.get("from") or "Unknown Sender"

                if "<" in sender:
                    sender = sender.split("<")[0].strip()

                return f"📧 Latest Email\nFrom: {sender}\nSubject: {subject}"

            else:
                return "You have no emails."

        return "You have emails in your inbox."

    # -------------------------------------------------
    # MULTI EMAIL
    # -------------------------------------------------

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

        return response.choices[0].message.content

    # -------------------------------------------------
    # NON EMAIL REQUEST
    # -------------------------------------------------

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_command}],
        max_tokens=120
    )

    return response.choices[0].message.content