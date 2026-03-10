from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def detect_spam_emails(emails):

    spam_emails = []

    for email in emails:

        subject = email.get("subject", "")
        body = email.get("body", "")

        prompt = f"""
You are an email spam classifier.

Classify the email as SPAM or NOT_SPAM.

SPAM includes:
- lottery or prize scams
- promotional giveaways
- referral reward programs
- crypto or investment scams
- phishing emails
- marketing promotions

NOT_SPAM includes:
- work emails
- meeting invitations
- internship communication
- recruiter or job opportunity emails
- internship/job application emails
- security alerts or account notifications
- password change alerts
- login alerts
- bank alerts
- GitHub, Google, or account security alerts
- normal professional communication

Subject: {subject}

Body:
{body}

Respond with ONLY one word:

SPAM
or
NOT_SPAM
"""

        try:

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a strict spam email classifier."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=5
            )

            result = response.choices[0].message.content.strip().upper()

            if result == "SPAM":
                spam_emails.append(email)

        except Exception as e:
            print("Spam detection error:", e)

    return spam_emails