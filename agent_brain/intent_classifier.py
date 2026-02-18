from transformers import pipeline

# Load zero-shot classification model
classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
    device=-1
)

INTENTS = [
    "read_email",
    "summarize_email",
    "read_calendar",
    "read_task",
    "general_question"
]


def classify_intent(user_input: str) -> str:
    """
    Hybrid intent classifier:
    1. Zero-shot classification
    2. Fallback rule-based detection
    """

    text = user_input.lower()

    # --------------------------
    # Rule-based quick detection
    # --------------------------
    if "email" in text or "mail" in text:
        return "read_email"

    if "calendar" in text or "meeting" in text:
        return "read_calendar"

    if "task" in text:
        return "read_task"

    if (
        "summarize" in text
        or "summarise" in text
    ):
        return "summarize_email"
    
    if any(phrase in text for phrase in [
        "daily summary",
        "today summary",
        "what do i have today",
        "what do i have",
        "today schedule",
        "what is my schedule today"
    ]):
        return "daily_summary"
    
    # --------------------------
    # Zero-shot classification
    # --------------------------
    try:
        result = classifier(user_input, INTENTS)

        predicted_intent = result["labels"][0]
        confidence = result["scores"][0]

        # Accept only if confident
        if confidence > 0.5:
            return predicted_intent

        return "general_question"

    except Exception as e:
        print("Intent classification error:", e)
        return "general_question"
