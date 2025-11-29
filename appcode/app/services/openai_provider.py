import os
from typing import Dict, List, Tuple

from openai import OpenAI

from app.core.settings import settings

_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def call_openai(messages: List[Dict]) -> Tuple[str, str]:
    response = _client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=0.3,
    )
    text = response.choices[0].message.content
    return text, settings.openai_model
