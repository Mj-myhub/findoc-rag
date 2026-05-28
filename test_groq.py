"""Verify the Groq key works and the configured model is live."""
from groq import Groq

from findoc_rag.config import GROQ_API_KEY, SETTINGS

if not GROQ_API_KEY:
    raise SystemExit("GROQ_API_KEY is empty. Put your key in the .env file.")

client = Groq(api_key=GROQ_API_KEY)

print("A few available models:")
for mid in sorted(m.id for m in client.models.list().data)[:15]:
    print("  -", mid)

model = SETTINGS["generation"]["model"]
print(f"\nTesting configured model: {model}")
resp = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Reply with exactly: hello from groq"}],
    temperature=0,
    max_tokens=20,
)
print("Response:", resp.choices[0].message.content)
