import re

def answer_question(question, emails):
    if not emails:
        return "I could not find any emails to answer that."

    question = question.lower()
    latest_email = emails[0]

    body = latest_email.get("body", "")
    subject = latest_email.get("subject", "")
    sender = latest_email.get("from", "")

    # -------------------------
    # WHO SENT THE EMAIL
    # -------------------------
    if "who" in question or "sender" in question:
        return f"The email was sent by {sender}."

    # -------------------------
    # SUBJECT OF EMAIL
    # -------------------------
    if "subject" in question:
        return f"The subject of the email is {subject}."

    # -------------------------
    # DATE / TIME EXTRACTION
    # -------------------------
    if "date" in question or "time" in question or "when" in question:
        lines = body.split(".")
        for line in lines:
            if re.search(r"\b(am|pm|ist|time|date|\\d{4}|\\d{1,2}:\\d{2})\b", line.lower()):
                return line.strip()

        return "The email mentions an assessment, but I could not clearly identify the exact date and time."

    # -------------------------
    # FALLBACK
    # -------------------------
    return "I read the email, but I could not find a clear answer to that question."

