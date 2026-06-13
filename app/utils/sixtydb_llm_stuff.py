"""60db LLM — peer of llmOS_stuff.

Exposes the same `generate_response(system_prompt, user_prompt)`
signature so generate_podcast.py is unchanged at call sites.
60db's chat completions endpoint is OpenAI-compatible, which matches
the shape llmOS_stuff already sends.

Reference: https://docs.60db.ai/api-reference/llm/chat-completion
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

DEFAULT_API_BASE = "https://api.60db.ai"
DEFAULT_MODEL = "60db-tiny"


def generate_response(system_prompt: str, user_prompt: str) -> str:
    """Send a chat completion to 60db and return the assistant content.

    Behaviourally identical to llmOS_stuff.generate_response so the
    podcast pipeline can swap providers via env switch alone.
    """
    api_key = os.getenv("SIXTYDB_API_KEY")
    if not api_key:
        raise RuntimeError("SIXTYDB_API_KEY environment variable not set")
    api_base = os.getenv("SIXTYDB_API_BASE", DEFAULT_API_BASE).rstrip("/")
    model = os.getenv("SIXTYDB_LLM_MODEL", DEFAULT_MODEL)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "temperature": 0.7,
        "top_k": 20,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        f"{api_base}/v1/chat/completions",
        json=payload,
        headers=headers,
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]
