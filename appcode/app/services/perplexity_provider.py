import os
from typing import Dict, List, Tuple

from openai import OpenAI

from app.core.settings import settings

_client = OpenAI(
    api_key=os.environ["PPLX_API_KEY"],
    base_url="https://api.perplexity.ai",
)


def call_perplexity(messages: List[Dict]) -> Tuple[str, str]:
    response = _client.chat.completions.create(
        model=settings.perplexity_model,
        messages=messages,
        temperature=0.3,
    )
    text = response.choices[0].message.content
    return text, settings.perplexity_model
