from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    provider: str = Field(..., description="openai | perplexity | gemini")
    conversation_id: Optional[str] = Field(None, description="Conversation id")
    message: str = Field(..., description="User message")
