import os
from openai import OpenAI
from supabase import create_client

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)


def generate_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    
    return response.data[0].embedding


def store_email_embedding(email_id, embedding):

    supabase.table("emails").update({
        "embedding": embedding
    }).eq("email_id", email_id).execute()


def search_similar_emails(query, user_id):

    query_embedding = generate_embedding(query)

    response = supabase.rpc(
        "match_emails",
        {
            "query_embedding": query_embedding,
            "match_threshold": 0.7,
            "match_count": 5,
            "user_id": user_id
        }
    ).execute()

    return response.data
def answer_email_question(question, user_id):

    emails = search_similar_emails(question, user_id)

    if not emails:
        return "I could not find any relevant emails."

    context = ""

    for email in emails:
        context += f"Subject: {email['subject']}\n"
        context += f"Sender: {email['sender']}\n"
        context += f"Summary: {email['summary']}\n\n"

    prompt = f"""
Use the following email summaries to answer the user's question.

Emails:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
def categorize_emails_by_topic(topic, user_id):

    results = search_similar_emails(topic, user_id)

    if not results:
        return []

    grouped = []

    for email in results:

        subject = email["subject"].lower()
        summary = email["summary"].lower()

        if topic.lower() in subject or topic.lower() in summary:

            grouped.append({
                "gmail_id": email["gmail_id"],
                "subject": email["subject"],
                "sender": email["sender"]
            })

    return grouped
def find_email_for_action(query, user_id):

    results = search_similar_emails(query, user_id)

    if not results:
        return None

    email = results[0]

    subject = email.get("subject")

    # If subject missing, create a short preview
    if not subject or subject == "No Subject":
        summary = email.get("summary", "")
        subject = summary[:60] + "..." if summary else "Email"

    return {
        "gmail_id": email.get("gmail_id"),
        "subject": subject,
        "sender": email.get("sender"),
        "summary": email.get("summary")
    }