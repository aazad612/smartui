import time
from typing import Dict, List

from google.cloud import firestore

from app.core.settings import settings

_client = firestore.Client(project=settings.project_id)


def save_message(
    conversation_id: str,
    provider: str,
    role: str,
    content: str,
    model: str,
) -> None:
    doc = {
        "conversation_id": conversation_id,
        "provider": provider,
        "role": role,
        "content": content,
        "model": model,
        "created_at": time.time(),
    }
    _client.collection(settings.firestore_collection).add(doc)


def load_history(conversation_id: str, limit: int | None = None) -> List[Dict]:
    query = (
        _client.collection(settings.firestore_collection)
        .where("conversation_id", "==", conversation_id)
        .order_by("created_at")
    )
    docs = list(query.stream())
    if limit is None:
        limit = settings.history_limit
    if limit and len(docs) > limit:
        docs = docs[-limit:]
    return [d.to_dict() for d in docs]


def build_messages(history: List[Dict]) -> List[Dict]:
    messages: List[Dict] = [
        {"role": "system", "content": "You are a helpful assistant."},
    ]
    for h in history:
        messages.append(
            {
                "role": h["role"],
                "content": h["content"],
            },
        )
    return messages
