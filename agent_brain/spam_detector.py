spam_keywords = [
    "win money",
    "lottery",
    "free gift",
    "click here",
    "limited time offer",
    "urgent action required",
    "crypto investment",
    "guaranteed profit",
    "claim reward",
    "you are selected",
    "congratulations you won",
    "risk free investment"
]


def detect_spam_emails(emails):

    spam = []

    for email in emails:

        subject = email.get("subject", "").lower()
        body = email.get("body", "").lower()

        for word in spam_keywords:

            if word in subject or word in body:
                spam.append(email)
                break

    return spam