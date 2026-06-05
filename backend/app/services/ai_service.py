"""AI service — Claude API integration with context injection."""
from __future__ import annotations
import json
import logging
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from anthropic import AsyncAnthropic

from ..config import settings
from ..models.ai_conversation import AIConversation, AIMessage
from ..prompts.system_prompt import SYSTEM_PROMPT, SYSTEM_PROMPT_WITHOUT_CONTEXT
from .market_service import market_service
from .portfolio_service import portfolio_service
from .item_service import item_service

logger = logging.getLogger(__name__)


class AIService:

    def __init__(self):
        self._client: Optional[AsyncAnthropic] = None

    @property
    def client(self) -> AsyncAnthropic:
        if self._client is None:
            self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        return self._client

    async def _build_context(
        self,
        db: AsyncSession,
        context_hints: Optional[dict],
        user_message: str,
    ) -> tuple[str, str, str]:
        """Build market, portfolio, and item context blocks."""
        market_context = "No current market data available."
        portfolio_context = "No portfolio data available."
        item_context = "No specific item data available."

        hints = context_hints or {}
        include_market = hints.get("include_market", False) or self._is_market_query(user_message)
        include_portfolio = hints.get("include_portfolio", False) or self._is_portfolio_query(user_message)
        item_ids = hints.get("item_ids", [])

        if include_market:
            try:
                overview = await market_service.get_overview()
                market_context = json.dumps(overview, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.error(f"Failed to build market context: {e}")

        if include_portfolio:
            try:
                summary = await portfolio_service.get_summary(db)
                portfolio_context = json.dumps(summary, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.error(f"Failed to build portfolio context: {e}")

        if item_ids:
            try:
                items = []
                for gid in item_ids[:5]:  # Limit to 5 items
                    detail = await item_service.get_detail(gid)
                    if detail:
                        items.append(detail)
                item_context = json.dumps(items, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.error(f"Failed to build item context: {e}")

        return market_context, portfolio_context, item_context

    def _is_market_query(self, message: str) -> bool:
        """Detect if message is about market conditions."""
        keywords = ["市场", "行情", "走势", "趋势", "指数", "涨跌", "大盘",
                    "market", "trend", "index", "overview"]
        msg = message.lower()
        return any(kw in msg for kw in keywords)

    def _is_portfolio_query(self, message: str) -> bool:
        """Detect if message is about user's portfolio."""
        keywords = ["持仓", "库存", "我的", "portfolio", "inventory", "盈亏",
                    "买了", "持有", "仓位"]
        msg = message.lower()
        return any(kw in msg for kw in keywords)

    async def _get_recent_messages(self, db: AsyncSession, conversation_id: int, limit: int = 10) -> list[AIMessage]:
        """Get recent messages from a conversation."""
        result = await db.execute(
            select(AIMessage)
            .where(AIMessage.conversation_id == conversation_id)
            .order_by(AIMessage.created_at.desc())
            .limit(limit)
        )
        return list(reversed(result.scalars().all()))

    async def chat(
        self,
        db: AsyncSession,
        message: str,
        conversation_id: Optional[int] = None,
        context_hints: Optional[dict] = None,
    ) -> AsyncGenerator[str, None]:
        """Send a message and stream the AI response."""

        # Create conversation if needed
        if conversation_id is None:
            conv = AIConversation(title=message[:50] if len(message) > 50 else message)
            db.add(conv)
            await db.commit()
            await db.refresh(conv)
            conversation_id = conv.id

        # Build context
        market_ctx, portfolio_ctx, item_ctx = await self._build_context(
            db, context_hints, message
        )

        # Assemble system prompt
        has_context = (
            "No current market data available" not in market_ctx or
            "No portfolio data available" not in portfolio_ctx or
            "No specific item data available" not in item_ctx
        )
        system_prompt = SYSTEM_PROMPT.format(
            market_context=market_ctx,
            portfolio_context=portfolio_ctx,
            item_context=item_ctx,
        )

        # Get recent history
        recent_messages = await self._get_recent_messages(db, conversation_id)

        # Assemble messages for Claude
        claude_messages = []
        for m in recent_messages:
            claude_messages.append({"role": m.role, "content": m.content})
        claude_messages.append({"role": "user", "content": message})

        # Store user message
        user_msg = AIMessage(
            conversation_id=conversation_id,
            role="user",
            content=message,
            context_json=json.dumps(context_hints or {}, ensure_ascii=False),
        )
        db.add(user_msg)
        await db.commit()

        # Actually implement streaming - we'll do a non-streaming call first for simplicity,
        # then upgrade to streaming later
        try:
            full_response = ""
            with self.client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=system_prompt,
                messages=claude_messages,
                temperature=0.7,
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    yield text

            # Store assistant message
            assistant_msg = AIMessage(
                conversation_id=conversation_id,
                role="assistant",
                content=full_response,
                context_json=json.dumps({
                    "market": market_ctx != "No current market data available.",
                    "portfolio": portfolio_ctx != "No portfolio data available.",
                    "item": item_ctx != "No specific item data available.",
                }, ensure_ascii=False),
                token_count=len(full_response) // 4,  # rough estimate
            )
            db.add(assistant_msg)

            # Update conversation title and timestamp
            result = await db.execute(select(AIConversation).where(AIConversation.id == conversation_id))
            conv = result.scalar_one_or_none()
            if conv:
                from datetime import datetime
                conv.updated_at = datetime.now().isoformat()
                if conv.title == "New Conversation":
                    conv.title = message[:50] if len(message) > 50 else message

            await db.commit()

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            yield f"\n\n*AI 服务暂时不可用，请稍后重试。错误信息: {str(e)}*"

    async def get_conversations(self, db: AsyncSession) -> list[AIConversation]:
        """List all conversations."""
        result = await db.execute(
            select(AIConversation).order_by(AIConversation.updated_at.desc())
        )
        return result.scalars().all()

    async def get_messages(self, db: AsyncSession, conversation_id: int) -> list[AIMessage]:
        """Get messages for a conversation."""
        result = await db.execute(
            select(AIMessage)
            .where(AIMessage.conversation_id == conversation_id)
            .order_by(AIMessage.created_at.asc())
        )
        return result.scalars().all()

    async def delete_conversation(self, db: AsyncSession, conversation_id: int) -> bool:
        """Delete a conversation."""
        result = await db.execute(
            select(AIConversation).where(AIConversation.id == conversation_id)
        )
        conv = result.scalar_one_or_none()
        if not conv:
            return False
        await db.delete(conv)
        await db.commit()
        return True


ai_service = AIService()
