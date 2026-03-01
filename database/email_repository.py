from database.db_client import supabase
from datetime import datetime

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

        parsed_date = datetime.strptime(
            cleaned_date,
            "%a, %d %b %Y %H:%M:%S %z"
        )

        # 🔥 Convert datetime → ISO string
        parsed_date = parsed_date.isoformat()

    except Exception as e:
        print("⚠ Date parsing failed:", e)
        parsed_date = None

    supabase.table("emails").insert({
        "gmail_id": gmail_id,
        "user_id": user_id,
        "subject": subject,
        "sender": sender,
        "received_at": parsed_date,  # now ISO string
        "summary": summary,
        "meeting": meeting,
        "tasks": tasks,
        "processed": True,
        "token_used": tokens_used
    }).execute()