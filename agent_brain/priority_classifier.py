def classify_priority(email: dict) -> str:
    """
    Classifies email into High, Medium, Low priority.
    """

    subject = email.get("subject", "").lower()
    sender = email.get("from", "").lower()
    body = email.get("body", "").lower()

    # High priority keywords
    high_keywords = [
        "urgent",
        "immediate",
        "deadline",
        "important",
        "action required",
        "final notice"
    ]

    # Medium priority keywords
    medium_keywords = [
        "reminder",
        "meeting",
        "update",
        "schedule"
    ]

    # Check High Priority
    if any(word in subject or word in body for word in high_keywords):
        return "High"

    # Important sender logic
    if "professor" in sender or "hr" in sender:
        return "High"

    # Check Medium Priority
    if any(word in subject or word in body for word in medium_keywords):
        return "Medium"

    return "Low"
