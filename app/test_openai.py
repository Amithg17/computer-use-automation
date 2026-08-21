import os

from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY was not found."
    )


# Create OpenAI client
client = OpenAI(
    api_key=api_key
)


# Make a minimal test request
response = client.responses.create(
    model="gpt-5.4-mini",
    input=(
        "Reply with exactly these words: "
        "LLM CONNECTION SUCCESSFUL"
    )
)


print()
print("===================================")
print("OPENAI API TEST")
print("===================================")
print(response.output_text)
print("===================================")