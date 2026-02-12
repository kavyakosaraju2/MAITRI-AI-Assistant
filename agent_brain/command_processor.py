def process_command(text):
    text = text.lower()

    if "read email" in text:
        return "READ_EMAILS"

    if "calendar" in text or "event" in text:
        return "READ_CALENDAR"

    if "task" in text or "assignment" in text:
        return "READ_TASKS"

    if "pending task" in text or "any task" in text:
        return "CHECK_TASKS"

    if "summary" in text:
        return "READ_SUMMARY"
    
    if "last email" in text or "latest email" in text:
        return "LAST_EMAIL"


    if "stop" in text or "exit" in text:
        return "STOP"

    return "QUESTION"





