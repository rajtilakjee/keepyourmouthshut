import requests
import os
from dotenv import load_dotenv

load_dotenv()

llmos_api_key = os.getenv("llmOS_API_KEY")

url = "https://api.llmos.dev/v1/chat/completions"


def generate_response(system_prompt, user_prompt):
    payload = {
        "model": "mistral-7b-instruct",
        "messages": [
            {"content": system_prompt, "role": "system", "name": "system"},
            {"content": user_prompt, "role": "user", "name": "user"},
        ],
        "max_tokens": 50,
        "temperature": 0.7,
        "top_p": 1.0,
        "presence_penalty": 0.0,
        "frequency_penalty": "0.0",
    }

    headers = {"Authorization": llmos_api_key, "Content-Type": "application/json"}

    response = requests.request("POST", url, json=payload, headers=headers)
    answer = response.json()

    result = answer["choices"][0]["message"]["content"]
    return result
