from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("Listing available models...\n")

models = client.models.list()

for m in models:
    print(m.name)