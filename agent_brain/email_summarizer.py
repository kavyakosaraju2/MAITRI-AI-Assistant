from transformers import pipeline

# Load summarization model ONCE
summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn",
    device=-1  # CPU
)

def summarize_email(email_text):
    if not email_text:
        return "This email has no readable content."

    cleaned_text = email_text.strip()

    # -----------------------------
    # SHORT EMAIL → READ IT
    # -----------------------------
    if len(cleaned_text) < 200:
        return f"This email says: {cleaned_text}"

    # -----------------------------
    # LONG EMAIL → SUMMARIZE
    # -----------------------------
    try:
        summary = summarizer(
            cleaned_text,
            max_length=120,
            min_length=40,
            do_sample=False
        )

        return summary[0]["summary_text"]

    except Exception:
        # Fallback safety
        return f"This email says: {cleaned_text[:300]}"




