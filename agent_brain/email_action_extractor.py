import dateparser
import spacy
import re

nlp = spacy.load("en_core_web_sm")


def extract_datetime_from_sentence(sentence: str, base_date=None):
    """
    Extract datetime from sentence using spaCy + dateparser.
    Interprets relative dates based on email sent date.
    """

    doc = nlp(sentence)

    date_text = None
    time_text = None

    for ent in doc.ents:
        if ent.label_ == "DATE":
            date_text = ent.text
        if ent.label_ == "TIME":
            time_text = ent.text

    settings = {}

    if base_date:
        settings = {"RELATIVE_BASE": base_date}

    if date_text and time_text:
        return dateparser.parse(
            f"{date_text} {time_text}",
            settings=settings
        )

    if date_text:
        return dateparser.parse(
            date_text,
            settings=settings
        )

    return None


def extract_actions_from_email(email_body: str, base_date=None):
    """
    Extract:
    - Meeting datetime
    - Action item bullets
    """

    result = {
        "meeting": None,
        "action_items": []
    }

    doc = nlp(email_body)

    deadline_datetime = None

    # -------------------------
    # Detect Meeting & Deadline
    # -------------------------
    for sentence in doc.sents:

        sentence_text = sentence.text.lower()

        if "meeting" in sentence_text:
            parsed_datetime = extract_datetime_from_sentence(
                sentence.text,
                base_date
            )
            if parsed_datetime:
                result["meeting"] = {
                    "title": "Meeting from Email",
                    "datetime": parsed_datetime
                }

        if "deadline" in sentence_text:
            parsed_datetime = extract_datetime_from_sentence(
                sentence.text,
                base_date
            )
            if parsed_datetime:
                deadline_datetime = parsed_datetime

    # -------------------------
    # Bullet Extraction (Safe Split)
    # -------------------------
    parts = email_body.split(" - ")

    for part in parts[1:]:

        stop_words = ["If you fail", "Let me know", "Best regards"]

        for stop in stop_words:
            if stop in part:
                part = part.split(stop)[0]

        cleaned_task = part.strip()

        if cleaned_task:
            result["action_items"].append({
                "title": cleaned_task,
                "due": deadline_datetime
            })

    return result
