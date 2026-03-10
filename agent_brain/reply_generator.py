import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_reply(email_summary, sender, user_instruction):

    sender_name = sender.split()[0]

    prompt = f"""
You are an AI email assistant.

Original email summary:
{email_summary}

The sender of the email is:
{sender}

The user wants to reply with this intent:
{user_instruction}

Write a clear and professional reply email.

Rules:
- Address the sender as: Dear {sender_name},
- Only include information relevant to the user's intent
- Do NOT repeat the entire email instructions
- Keep the reply concise and natural
- End with: Best regards, Kavya
- Do not use placeholders like [Name]

Write only the email body.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()