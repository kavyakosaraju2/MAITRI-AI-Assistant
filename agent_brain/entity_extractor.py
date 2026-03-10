import spacy
from datetime import datetime, timedelta
from dateutil import parser

# Load English model
nlp = spacy.load("en_core_web_sm")


MEETING_KEYWORDS = [
    "meeting",
    "call",
    "zoom",
    "google meet",
    "meet",
    "discussion",
    "appointment"
]


def extract_entities(text: str) -> dict:

    text_lower = text.lower()

    now = datetime.now()

    if "day after tomorrow" in text_lower:
        base_date = now + timedelta(days=2)
        date_str = base_date.strftime("%Y-%m-%d")

    elif "tomorrow" in text_lower:
        base_date = now + timedelta(days=1)
        date_str = base_date.strftime("%Y-%m-%d")

    elif "today" in text_lower:
        date_str = now.strftime("%Y-%m-%d")

    else:
        date_str = None

    try:

        parsed = parser.parse(text, fuzzy=True)

        if date_str:
            parsed = parsed.replace(
                year=int(date_str[:4]),
                month=int(date_str[5:7]),
                day=int(date_str[8:10])
            )

        return {
            "date": parsed.date().isoformat(),
            "time": parsed.time().isoformat(),
            "datetime": parsed.strftime("%Y-%m-%dT%H:%M:%S")
        }

    except Exception:
        return {"date": None, "time": None, "datetime": None}