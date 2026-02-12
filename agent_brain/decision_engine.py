def decide_response(intent, emails, events, tasks):
    """
    Step 6: Decide WHAT to say, not just WHAT to do
    """

    if intent == "READ_EMAILS":
        if not emails:
            return "You have no new emails."

        important = emails[0]
        subject = important.get("subject", "No subject")
        sender = important.get("from", "Unknown sender")

        return f"Your latest email is from {sender}. The subject is {subject}."

    elif intent == "READ_CALENDAR":
        if not events:
            return "You have no upcoming calendar events."

        event = events[0]
        return f"You have an upcoming event starting at {event.get('start')}."

    elif intent == "READ_TASKS":
        if not tasks:
            return "You have no pending tasks."

        return f"You have {len(tasks)} pending tasks."

    elif intent == "READ_SUMMARY":
        return (
            f"You have {len(emails)} emails, "
            f"{len(events)} calendar events, "
            f"and {len(tasks)} tasks today."
        )

    else:
        return "I understood your words, but I am not sure what action to take."
