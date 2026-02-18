from agent_brain.intent_classifier import classify_intent
from agent_brain.entity_extractor import extract_entities
from agent_brain.priority_classifier import classify_priority
from agent_brain.context_memory import memory
from agent_brain.email_action_extractor import extract_actions_from_email
from calendar_agent.calendar_reader import create_calendar_event
from task_agent.task_reader import create_task
import dateparser
from datetime import datetime
from datetime import timezone

def filter_today_items(emails, events, tasks):

    today = datetime.now().date()

    # -------------------------
    # EMAILS
    # -------------------------
    today_emails = []
    for email in emails:
        email_date_raw = email.get("date")

        if isinstance(email_date_raw, str):
            parsed = dateparser.parse(email_date_raw)
        elif isinstance(email_date_raw, datetime):
            parsed = email_date_raw
        else:
            parsed = None

        if parsed and parsed.date() == today:
            today_emails.append(email)

    # -------------------------
    # EVENTS
    # -------------------------
    today_events = []
    for event in events:

        start_raw = None

        # Handle Google Calendar structure
        if isinstance(event.get("start"), dict):
            start_raw = event["start"].get("dateTime") or event["start"].get("date")
        else:
            start_raw = event.get("start")

        if isinstance(start_raw, str):
            parsed = dateparser.parse(start_raw)
        elif isinstance(start_raw, datetime):
            parsed = start_raw
        else:
            parsed = None

        if parsed and parsed.date() == today:
            today_events.append(event)

    # -------------------------
    # TASKS
    # -------------------------
    today_tasks = []
    for task in tasks:
        due_raw = task.get("due")

        if isinstance(due_raw, str):
            parsed = dateparser.parse(due_raw)
        elif isinstance(due_raw, datetime):
            parsed = due_raw
        else:
            parsed = None

        if parsed and parsed.date() == today:
            today_tasks.append(task)

    return today_emails, today_events, today_tasks

def decide_response(user_input, emails, events, tasks):

    # ---------------------------------
    # HANDLE CONFIRMATION FIRST
    # ---------------------------------
    if memory.pending_action:

        text = user_input.lower()

        if "yes" in text:

            action = memory.pending_action
            memory.pending_action = None

            if action["type"] == "combined":

                # Add meeting
                if action["meeting"]:
                    create_calendar_event(
                        action["creds"],
                        action["meeting"]["title"],
                        action["meeting"]["datetime"]
                    )

                # Add tasks
                if action["tasks"]:
                    for task in action["tasks"]:
                        create_task(
                            action["creds"],
                            task["title"],
                            task["due"]
                        )

                return "Meeting and tasks added successfully."

        elif "no" in text:
            memory.pending_action = None
            return "Okay, I will not add them."

    # ---------------------------------
    # INTENT CLASSIFICATION
    # ---------------------------------
    intent = classify_intent(user_input)
    entities = extract_entities(user_input)

    # ---------------------------------
    # EMAIL READING
    # ---------------------------------
    if intent == "read_email":

        if not emails:
            return "You have no new emails."

        latest = emails[0]
        priority = classify_priority(latest)

        memory.last_email = latest

        return (
            f"Your latest email is from {latest.get('from')}. "
            f"The subject is '{latest.get('subject')}'. "
            f"This email is marked as {priority} priority."
        )

    # ---------------------------------
    # SUMMARIZATION + ACTION DETECTION
    # ---------------------------------
 
    elif intent == "summarize_email":

        from agent_brain.email_summarizer import summarize_email

        if not memory.last_email:
            return "There is no email to summarize."

        print("EMAIL OBJECT:", memory.last_email)
        
        email_body = memory.last_email.get("body", "")

        summary = summarize_email(email_body)

        import dateparser

        email_date = memory.last_email.get("date")

        base_date = None
        if email_date:
            base_date = dateparser.parse(email_date)

        actions = extract_actions_from_email(email_body, base_date)

        meeting = actions.get("meeting")
        action_items = actions.get("action_items")

        detected = []

        if meeting and meeting.get("datetime"):
            detected.append("meeting")

        if action_items:
            detected.append("tasks")

        if detected:

            memory.pending_action = {
                "type": "combined",
                "meeting": meeting,
                "tasks": action_items,
                "creds": memory.creds
            }

            message = summary + "\n\nI detected:\n"

            if meeting:
                message += f"- A meeting on {meeting['datetime']}\n"

            if action_items:
                message += f"- {len(action_items)} action items\n"

            message += "\nShould I add them to your calendar and task list?"

            return message

        return summary

    elif intent == "daily_summary":

        today_emails, today_events, today_tasks = filter_today_items(
            emails, events, tasks
        )

        response = (
            f"Today you have {len(today_emails)} new emails, "
            f"{len(today_events)} events, "
            f"and {len(today_tasks)} tasks due."
        )

        return response

    # ---------------------------------
    # DEFAULT FALLBACK
    # ---------------------------------
    return "I understood your words, but I am not sure what action to take."
