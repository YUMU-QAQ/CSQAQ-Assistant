"""AI assistant API routes."""
import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.common import ApiResponse
from ..schemas.ai import ChatRequest
from ..database import get_db
from ..services.ai_service import ai_service

router = APIRouter(prefix="/api/v1/ai", tags=["AI"])


@router.get("/conversations")
async def get_conversations(db: AsyncSession = Depends(get_db)):
    """List conversation history."""
    convs = await ai_service.get_conversations(db)
    return ApiResponse.ok([
        {
            "id": c.id,
            "title": c.title,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
        }
        for c in convs
    ])


@router.post("/conversations")
async def create_conversation(db: AsyncSession = Depends(get_db)):
    """Create new conversation."""
    from ..models.ai_conversation import AIConversation
    conv = AIConversation()
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return ApiResponse.ok({
        "id": conv.id,
        "title": conv.title,
        "created_at": conv.created_at,
    })


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: int, db: AsyncSession = Depends(get_db)):
    """Get messages for a conversation."""
    messages = await ai_service.get_messages(db, conversation_id)
    return ApiResponse.ok([
        {
            "id": m.id,
            "conversation_id": m.conversation_id,
            "role": m.role,
            "content": m.content,
            "context_json": m.context_json,
            "created_at": m.created_at,
        }
        for m in messages
    ])


@router.post("/chat")
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Send message and get AI response (streaming)."""
    async def generate():
        async for chunk in ai_service.chat(
            db=db,
            message=req.message,
            conversation_id=req.conversation_id,
            context_hints=req.context_hints.model_dump() if req.context_hints else None,
        ):
            yield chunk

    return StreamingResponse(
        generate(),
        media_type="text/plain; charset=utf-8",
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a conversation."""
    ok = await ai_service.delete_conversation(db, conversation_id)
    if not ok:
        return ApiResponse.error(404, "Conversation not found")
    return ApiResponse.ok(None, "Deleted")
