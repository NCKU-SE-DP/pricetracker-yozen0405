from openai import OpenAI
from .config import ai_config

def generate_ai_response(content, prompt):
    message = [
        {
            "role": "system",
            "content": prompt,
        },
        {"role": "user", "content": f"{content}"},
    ]

    completion = OpenAI(api_key=ai_config.OPEN_AI_KEY).chat.completions.create(
        model=ai_config.OPEN_AI_MODEL,
        messages=message,
    )
    return completion.choices[0].message.content