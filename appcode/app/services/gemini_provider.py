import os
from typing import Dict, List, Tuple

from openai import OpenAI

from app.core.settings import settings

_client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/openai/v1",
)


def call_gemini(messages: List[Dict]) -> Tuple[str, str]:
    response = _client.chat.completions.create(
        model=settings.gemini_model,
        messages=messages,
        temperature=0.3,
    )
    text = response.choices[0].message.content
    return text, settings.gemini_model
