from transformers import BartForConditionalGeneration, BartTokenizer
import torch

# -----------------------------
# Load Model and Tokenizer ONCE
# -----------------------------

MODEL_NAME = "facebook/bart-large-cnn"

tokenizer = BartTokenizer.from_pretrained(MODEL_NAME)
model = BartForConditionalGeneration.from_pretrained(MODEL_NAME)

device = torch.device("cpu")
model = model.to(device)


def summarize_email(email_text: str) -> str:
    """
    Summarizes email using BART model.
    """

    if not email_text:
        return "This email has no readable content."

    cleaned_text = email_text.strip()

    # Short email → Just read it
    if len(cleaned_text) < 200:
        return f"This email says: {cleaned_text}"

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

        return summary

    except Exception as e:
        print("Summarization error:", e)
        return f"This email says: {cleaned_text[:300]}"
