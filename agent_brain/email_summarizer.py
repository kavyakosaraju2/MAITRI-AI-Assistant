from transformers import pipeline

# Load summarization model
summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)

def summarize_email(email_text):
    if not email_text or len(email_text.strip()) < 50:
        return "Email content is too short to summarize."

    # 🔹 VERY IMPORTANT: limit input size
    max_input_length = 1000
    email_text = email_text[:max_input_length]

    summary = summarizer(
        email_text,
        max_length=60,
        min_length=20,
        do_sample=False
    )

    return summary[0]["summary_text"]


