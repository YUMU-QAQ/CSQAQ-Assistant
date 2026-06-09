"""Feishu Bot webhook routes."""
import json
import logging
from fastapi import APIRouter, Request, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..config import settings
from ..services.feishu_service import feishu_bot, feishu_pusher
from ..schemas.common import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/feishu", tags=["Feishu"])


@router.get("/webhook")
async def verify_webhook(
    challenge: str = Query("", description="Feishu verification challenge"),
    token: str = Query("", description="Verification token"),
):
    """
    Feishu webhook URL verification.
    When configuring the bot in Feishu Open Platform, Feishu sends a GET
    request with a challenge parameter. We must return the challenge value.
    """
    logger.info(f"Feishu webhook verification: challenge={challenge[:20]}...")
    return {"challenge": challenge}


@router.post("/webhook")
async def handle_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Receive and process messages from Feishu bot.
    """
    try:
        body = await request.json()
        logger.info(f"Feishu webhook received: {json.dumps(body, ensure_ascii=False)[:500]}")
    except Exception:
        return {"code": 400, "msg": "Invalid JSON"}

    # Handle URL verification (sometimes Feishu uses POST for this too)
    if body.get("type") == "url_verification":
        challenge = body.get("challenge", "")
        return {"challenge": challenge}

    # Parse event
    event = body.get("event", {})
    if not event:
        # Some Feishu bot setups use a different format
        header = body.get("header", {})
        event_type = header.get("event_type", "")
        event = body.get("event", body)

    # Get message content
    message_type = event.get("message_type", "")
    msg_id = event.get("message_id", "")

    # Skip messages from bot itself to avoid loops
    sender = event.get("sender", {})
    sender_id = sender.get("sender_id", "") if isinstance(sender, dict) else ""

    # Get text content
    content_text = ""
    if message_type == "text":
        content_text = event.get("text", "")
    elif "content" in body:
        content_raw = body.get("content", body)
        if isinstance(content_raw, dict):
            content_text = content_raw.get("text", "")
        elif isinstance(content_raw, str):
            try:
                content_obj = json.loads(content_raw)
                content_text = content_obj.get("text", content_raw)
            except json.JSONDecodeError:
                content_text = content_raw
    else:
        # Try to extract any text from the event
        content_text = event.get("text", str(body))

    if not content_text:
        # Acknowledge but don't reply to empty messages
        return {"code": 0}

    # Get user name
    user_name = "User"
    if isinstance(sender, dict):
        user_name = sender.get("sender_name", sender.get("sender_id", "User"))

    # Process message through bot
    logger.info(f"Feishu message from {user_name}: {content_text[:100]}")

    reply = await feishu_bot.handle_message(db, content_text, user_name)

    return reply


@router.post("/push/test")
async def test_push(message: str = "🎉 CSQAQ 飞书机器人测试推送成功！"):
    """Test Feishu push notification."""
    ok = await feishu_pusher.push_message(message)
    return ApiResponse.ok({"success": ok, "message": "推送成功" if ok else "推送失败，请检查 webhook URL 配置"})


@router.post("/push/alerts")
async def push_alerts(db: AsyncSession = Depends(get_db)):
    """Manually trigger alert check and push."""
    triggered = await feishu_pusher.check_and_push_alerts(db)
    return ApiResponse.ok({
        "triggered_count": len(triggered),
        "alerts": triggered,
    })
