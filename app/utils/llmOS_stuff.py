import requests
from dotenv import load_dotenv
import os

load_dotenv()

llmos_api_key = os.getenv("llmOS_API_KEY")

url = "https://api.llmos.dev/v1/chat/completions"


def generate_response(system_prompt, user_prompt):
    """
    Generate a response using the Mistral-7B instructive language model.

    Args:
        system_prompt (str): System prompt for instructing the language model.
        user_prompt (str): User prompt to guide the language model's response.

    Returns:
        str: The generated response from the language model.

    This function sends a request to the Mistral-7B instructive language model API with the
    provided system and user prompts. The generated response is extracted from the API
    response and returned.

    Note:
        - The Mistral-7B API key (llmos_api_key) and API endpoint (url) should be defined
          before calling this function.

    Example:
        response = generate_response("Provide information about", "What is the process of")
        print(response)
    """
    payload = {
        "model": "mistral-7b-instruct",
        "messages": [
            {"content": system_prompt, "role": "system", "name": "system"},
            {"content": user_prompt, "role": "user", "name": "user"},
        ],
        "temperature": 0.7,
    }

    headers = {"Authorization": llmos_api_key, "Content-Type": "application/json"}

    response = requests.request("POST", url, json=payload, headers=headers)
    answer = response.json()

    result = answer["choices"][0]["message"]["content"]
    return result
