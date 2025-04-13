import json
import requests
import os
from dotenv import load_dotenv
import time
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

def call_language_model(prompt: str):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-r1-distill-llama-70b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 1000,
        "stream": True
    }

    response = requests.post(GROQ_ENDPOINT, headers=headers, json=payload, stream=True)

    def stream_response():
        for line in response.iter_lines():
            if line and line.startswith(b"data: "):
                line = line[len(b"data: "):]
                if line.strip() == b"[DONE]":
                    break
                try:
                    data = json.loads(line.decode("utf-8"))
                    content = data.get("choices", [{}])[0].get("delta", {}).get("content")
                    if content:
                        yield content
                        time.sleep(0.01)
                except Exception:
                    continue

    return stream_response()
