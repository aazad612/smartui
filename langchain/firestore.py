# firestore_store.py
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from google.cloud import firestore

from dotenv import load_dotenv
load_dotenv()


def get_client() -> firestore.Client:
    # Uses GOOGLE_APPLICATION_CREDENTIALS / ADC
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    return firestore.Client(project=project_id)


def create_task(
    title: str,
    status: str = "open",
    priority: str = "P3",
    meta: Dict[str, Any] | None = None,
) -> str:
    client = get_client()
    doc_ref = client.collection("tasks").document()
    payload = {
        "title": title,
        "status": status,
        "priority": priority,
        "created_at": datetime.now(timezone.utc),
        "meta": meta or {},
    }
    doc_ref.set(payload)
    return doc_ref.id


def update_task(task_id: str, updates: Dict[str, Any]) -> None:
    client = get_client()
    client.collection("tasks").document(task_id).update(updates)


def list_tasks(limit: int = 20, status: str | None = None) -> List[Dict[str, Any]]:
    client = get_client()
    col = client.collection("tasks").order_by("created_at", direction=firestore.Query.DESCENDING)
    if status:
        col = col.where("status", "==", status)
    docs = col.limit(limit).stream()
    results: List[Dict[str, Any]] = []
    for d in docs:
        data = d.to_dict()
        data["id"] = d.id
        results.append(data)
    return results
