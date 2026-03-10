from transformers import BartForConditionalGeneration, BartTokenizer
import torch
import re
from datetime import datetime

# -----------------------------
# Load Model and Tokenizer ONCE
# -----------------------------

MODEL_NAME = "facebook/bart-large-cnn"

tokenizer = BartTokenizer.from_pretrained(MODEL_NAME)
model = BartForConditionalGeneration.from_pretrained(MODEL_NAME)

device = torch.device("cpu")
model = model.to(device)


# -------------------------------------------------
# MEETING EXTRACTION (FIXED AM/PM HANDLING)
# -------------------------------------------------

def extract_meeting(text):

    pattern = r"(\w+\s\d{1,2},?\s\d{4}?)\s*(?:at)?\s*(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)"

    match = re.search(pattern, text)

    if not match:
        return None

    date_str = match.group(1).replace(",", "")
    time_str = match.group(2)

    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%B %d %Y %I:%M %p")

        return {
            "title": "Client Review Meeting",
            "datetime": dt.strftime("%Y-%m-%d %H:%M")
        }

    except:
        return None
def extract_tasks(text):

    tasks = []

    # detect numbered tasks like "1. task"
    pattern = r"\d+\.\s*([A-Za-z].+)"

    matches = re.findall(pattern, text)

    for m in matches:
        task = m.strip()

        if len(task) > 3:
            tasks.append({
                "title": task,
                "due": None
            })

    return tasks

# -------------------------------------------------
# EMAIL SUMMARIZATION
# -------------------------------------------------

def summarize_email(email_text: str):
    """
    Summarizes email using BART model.
    Returns: summary, meeting, tasks, tokens
    """

    if not email_text:
        return "This email has no readable content.", None, [], 0

    cleaned_text = email_text.strip()

    # Short email → Just read it
    if len(cleaned_text) < 200:

        summary = f"This email says: {cleaned_text}"

        meeting = extract_meeting(cleaned_text)
        tasks = extract_tasks(cleaned_text)

        #print("MEETING DETECTED:", meeting)
        #print("TASKS DETECTED:", tasks)

        return summary, meeting, tasks, 0

    try:

        inputs = tokenizer(
            cleaned_text,
            max_length=1024,
            return_tensors="pt",
            truncation=True
        )

        summary_ids = model.generate(
            inputs["input_ids"].to(device),
            max_length=150,
            min_length=40,
            length_penalty=2.0,
            num_beams=4,
            early_stopping=True
        )

        summary = tokenizer.decode(
            summary_ids[0],
            skip_special_tokens=True
        )

        # Detect meeting from email
        meeting = extract_meeting(cleaned_text)
        tasks = extract_tasks(cleaned_text)

        #print("MEETING DETECTED:", meeting)
        

        return summary, meeting, tasks, 0

    except Exception as e:

        print("Summarization error:", e)

        tasks = extract_tasks(cleaned_text)

    summary = f"This email says: {cleaned_text[:300]}"

    tasks = extract_tasks(cleaned_text)

    return summary, meeting, tasks, 0
