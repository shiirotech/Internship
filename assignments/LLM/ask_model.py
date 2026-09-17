import os
from dotenv import load_dotenv
from datetime import date
from pathlib import Path
from ollama import Client
from .schema import ParsedTask

load_dotenv()

CURRENT_DATE = date.today().isoformat()
PROMPT_PATH = Path(__file__).parent / "parse_text_prompt.md"

client = Client(host=os.getenv("OLLAMA_URL"))

def ask(text: str) -> str:
    prompt = PROMPT_PATH.read_text()

    response = client.chat(
        model=os.getenv("OLLAMA_MODEL"),
        messages=[
            {
                "role": "system",
                "content": f"{prompt}\n\nCurrent date: {CURRENT_DATE}"
            },
            {
                "role": "user",
                "content": text
            }
        ],
        format=ParsedTask.model_json_schema()
    )

    return response["message"]["content"]