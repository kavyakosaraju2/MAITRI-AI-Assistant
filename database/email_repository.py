from database.db_client import supabase
from datetime import datetime
from agent_brain.embedding_service import generate_embedding

def email_exists(gmail_id):
    response = supabase.table("emails") \
        .select("*") \
        .eq("gmail_id", gmail_id) \
        .execute()

    return len(response.data) > 0


def get_email(gmail_id):
    response = supabase.table("emails") \
        .select("*") \
        .eq("gmail_id", gmail_id) \
        .execute()

    if response.data:
        return response.data[0]
    return None

def save_email_result(user_id, gmail_id, subject, sender,
                      received_at, summary, meeting, tasks, tokens_used):

    try:
        cleaned_date = received_at.split(" (")[0]

        try:
            parsed_date = datetime.strptime(
                cleaned_date,
                "%a, %d %b %Y %H:%M:%S %z"
            )
        except:
            parsed_date = datetime.strptime(
                cleaned_date,
                "%a, %d %b %Y %H:%M:%S %Z"
            )

        parsed_date = parsed_date.isoformat()

    except Exception as e:
        print("⚠ Date parsing failed:", e)
        parsed_date = None

    if summary:
        embedding = generate_embedding(subject + " " + summary)
    else:
        embedding = None

    supabase.table("emails").insert({
        "gmail_id": gmail_id,
        "user_id": user_id,
        "subject": subject,
        "sender": sender,
        "received_at": parsed_date,
        "summary": summary,
        "meeting": meeting,
        "tasks": tasks,
        "processed": True,
        "token_used": tokens_used,
        "embedding": embedding
    }).execute()
def get_email_meetings(user_id):

    response = supabase.table("emails") \
        .select("meeting") \
        .eq("user_id", user_id) \
        .not_.is_("meeting", "null") \
        .execute()

    meetings = []

    for row in response.data:
        if row["meeting"]:
            meetings.append(row["meeting"])

    return meetings