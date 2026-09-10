import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(base_url=os.getenv("OLLAMA_URL") + "/v1", api_key="ollama")

res = client.chat.completions.create(
    model=os.getenv("OLLAMA_MODEL"),
    messages=[
        {
            "role": "user",
            "content": "Reply with exactly the word: ready"
        }
    ]
)

print(res.choices[0].message.content)