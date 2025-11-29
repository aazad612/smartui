from pathlib import Path
import uuid

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse

from app.core.models import ChatRequest
from app.services.firestore_store import load_history, save_message, build_messages
from app.services.openai_provider import call_openai

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    root = Path(__file__).resolve().parents[2]
    html_path = root / "web" / "templates" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@router.post("/chat")
async def chat_endpoint(req: ChatRequest):
    # Always OpenAI, so provider becomes irrelevant
    conversation_id = req.conversation_id or str(uuid.uuid4())

    # Load + prepare history
    history = load_history(conversation_id)
    messages = build_messages(history)

    # Add user message
    messages.append({"role": "user", "content": req.message})
    save_message(conversation_id, "openai", "user", req.message, model="n/a")

    # --- OPENAI ONLY ---
    try:
        reply_text, model_used = call_openai(messages)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"OpenAI provider error: {str(e)}"},
        )

    # Save assistant reply
    save_message(conversation_id, "openai", "assistant", reply_text, model_used)

    return {
        "conversation_id": conversation_id,
        "reply": reply_text,
        "provider": "openai",
        "model": model_used,
    }
