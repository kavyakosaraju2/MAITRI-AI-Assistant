import re


# -------------------------------------------------
# HELPER: Get Latest Email
# -------------------------------------------------
def get_latest_email(emails):
    if not emails:
        return None
    return emails[0]


# -------------------------------------------------
# HELPER: Search Email By Keyword
# -------------------------------------------------
def search_email_by_keyword(emails, keyword):
    for email in emails:
        subject = email.get("subject", "").lower()
        body = email.get("body", "").lower()

        if keyword.lower() in subject or keyword.lower() in body:
            return email

    return None


# -------------------------------------------------
# HELPER: Extract Keyword From Question
# -------------------------------------------------
def extract_keyword(question):
    ignore_words = [
        "who", "what", "when", "is", "the", "a", "an",
        "did", "i", "my", "about", "was", "sent",
        "email", "mail", "latest", "last"
    ]

    words = question.lower().split()
    filtered = [word for word in words if word not in ignore_words]

    if filtered:
        return filtered[-1]

    return None


# -------------------------------------------------
# MAIN ANSWER FUNCTION
# -------------------------------------------------
def answer_question(question, emails):
    if not emails:
        return "I could not find any emails."

    question = question.lower()

    # -------------------------------------------------
    # 1️⃣ LATEST EMAIL QUESTIONS
    # -------------------------------------------------
    if "latest" in question or "last" in question:

        latest_email = get_latest_email(emails)

        if not latest_email:
            return "No emails found."

        sender = latest_email.get("from", "Unknown sender")
        subject = latest_email.get("subject", "No subject")

        if "who" in question or "sent" in question:
            return f"The latest email was sent by {sender}."

        if "subject" in question:
            return f"The subject of the latest email is {subject}."

        return f"Your latest email was sent by {sender} with subject {subject}."

    # -------------------------------------------------
    # 2️⃣ KEYWORD BASED SEARCH
    # -------------------------------------------------
    keyword = extract_keyword(question)

    if keyword:
        found_email = search_email_by_keyword(emails, keyword)

        if found_email:
            sender = found_email.get("from", "Unknown sender")
            subject = found_email.get("subject", "No subject")

            if "who" in question:
                return f"The email about {keyword} was sent by {sender}."

            if "subject" in question:
                return f"The subject of the email about {keyword} is {subject}."

            return f"I found an email about {keyword}. It was sent by {sender} with subject {subject}."

    # -------------------------------------------------
    # 3️⃣ DATE / TIME EXTRACTION FROM ALL EMAILS
    # -------------------------------------------------
    if "date" in question or "time" in question or "when" in question:

        for email in emails:
            body = email.get("body", "")

            lines = body.split(".")
            for line in lines:
                if re.search(r"\b(am|pm|ist|time|date|\d{4}|\d{1,2}:\d{2})\b", line.lower()):
                    return line.strip()

        return "I could not find any clear date or time information in your emails."

    # -------------------------------------------------
    # FALLBACK
    # -------------------------------------------------
    return "I searched your emails but could not find a clear answer."


