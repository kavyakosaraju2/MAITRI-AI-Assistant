def process_command(text):
    text = text.lower()

    # ---------------- CORE COMMANDS ----------------

    if "read email" in text:
        return "READ_EMAILS"

    if "calendar" in text or "event" in text:
        return "READ_CALENDAR"

    if "pending task" in text:
        return "CHECK_TASKS"

    if "task" in text or "assignment" in text:
        return "READ_TASKS"

    if "summary" in text:
        return "READ_SUMMARY"

    if "stop" in text or "exit" in text or "quit" in text:
        return "STOP"

    
    return "QUESTION"






