"""AI chat schemas."""
from typing import Optional, List
from pydantic import BaseModel


class ContextHints(BaseModel):
    """Hints for AI context injection."""
    item_ids: Optional[List[str]] = None
    include_portfolio: bool = False
    include_market: bool = False


class ChatRequest(BaseModel):
    """AI chat request."""
    conversation_id: Optional[int] = None
    message: str
    context_hints: Optional[ContextHints] = None


class ConversationResponse(BaseModel):
    """Conversation metadata."""
    id: int
    title: str
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    """Chat message."""
    id: int
    conversation_id: int
    role: str  # user, assistant
    content: str
    context_json: Optional[str] = None
    created_at: str
