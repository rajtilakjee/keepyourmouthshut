import time

import openai


def generate_response(system_prompt, user_prompt):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.7,
    )
    result = response.choices[0].message.content
    time.sleep(60)
    return result
