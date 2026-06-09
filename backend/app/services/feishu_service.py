"""Feishu Bot Service — message handling + notification push."""
from __future__ import annotations
import json
import logging
import httpx
from typing import Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from .market_service import market_service
from .item_service import item_service
from .ranking_service import ranking_service
from .portfolio_service import portfolio_service
from .alert_service import alert_service
from .ai_service import ai_service

logger = logging.getLogger(__name__)

# ============================================================
# Message Handling
# ============================================================

class FeishuBot:

    async def handle_message(self, db: AsyncSession, content: str, user_name: str = "") -> dict:
        """Process incoming Feishu message and return reply card."""
        text = content.strip().lower()

        # Strip @bot mention
        if text.startswith("@") and " " in text:
            text = text.split(" ", 1)[1]

        # Command routing
        if text.startswith("/price") or text.startswith("/p "):
            return await self._cmd_price(text)
        elif text.startswith("/search") or text.startswith("/s "):
            return await self._cmd_search(text)
        elif text.startswith("/rank") or text.startswith("/r "):
            return await self._cmd_rank(text)
        elif text.startswith("/portfolio") or text.startswith("/pf"):
            return await self._cmd_portfolio(db)
        elif text.startswith("/alert") or text.startswith("/a "):
            return await self._cmd_alert(text)
        elif text.startswith("/market") or text.startswith("/m"):
            return await self._cmd_market()
        elif text.startswith("/help"):
            return self._help_card()
        else:
            # Default: AI chat
            return await self._cmd_ai(db, text, user_name)

    # ---- Commands ----

    async def _cmd_price(self, text: str) -> dict:
        """查询饰品价格 /price <name>"""
        query = text.replace("/price", "").replace("/p ", "").strip()
        if not query:
            return self._error_card("请输入饰品名称，如: /price AK-47 | Redline")

        try:
            items = await item_service.search(query, limit=3)
            if not items:
                return self._error_card(f"未找到「{query}」相关饰品")

            fields = []
            for item in items[:3]:
                detail = await item_service.get_detail(str(item.get("good_id", "")))
                prices = detail.get("prices", {}) if detail else {}
                bu_price = prices.get("BUFF", {}).get("sell_price", "N/A") if isinstance(prices, dict) else "N/A"
                price_str = f"¥{bu_price:.2f}" if isinstance(bu_price, (int, float)) else str(bu_price)
                fields.append({
                    "is_short": False,
                    "text": {
                        "tag": "lark_md",
                        "content": f"**{item.get('name', 'N/A')}**\n价格: {price_str}\nID: `{item.get('good_id', '')}`"
                    }
                })

            return {
                "msg_type": "interactive",
                "card": {
                    "header": {"title": {"tag": "plain_text", "content": f"🔍 「{query}」查询结果"}, "template": "green"},
                    "elements": [
                        {"tag": "div", "fields": fields},
                        {"tag": "hr"},
                        {"tag": "note", "elements": [{"tag": "plain_text", "content": "数据来源: CSQAQ API"}]}
                    ]
                }
            }
        except Exception as e:
            return self._error_card(f"查询失败: {str(e)}")

    async def _cmd_search(self, text: str) -> dict:
        """搜索饰品"""
        return await self._cmd_price(text)  # same logic

    async def _cmd_rank(self, text: str) -> dict:
        """排行榜"""
        filter_type = "gainers"
        filters = {"涨幅": "gainers", "跌幅": "losers", "成交": "volume", "市值": "market_cap", "热度": "hot", "挂刀": "arbitrage"}
        for k, v in filters.items():
            if k in text:
                filter_type = v
                break

        try:
            data = await ranking_service.get_rankings(page=1, page_size=8, filter_type=filter_type)
            items = data.get("items", data) if isinstance(data, dict) else []
            items_list = items if isinstance(items, list) else items.get("items", []) if isinstance(items, dict) else []

            lines = []
            for i, item in enumerate(items_list[:8]):
                name = item.get("name", "N/A") if isinstance(item, dict) else "N/A"
                price = item.get("price", 0) if isinstance(item, dict) else 0
                change = item.get("change_pct", 0) if isinstance(item, dict) else 0
                sign = "+" if change >= 0 else ""
                lines.append(f"{i+1}. {name} | ¥{price:.2f} | {sign}{change}%")

            filter_labels = {"gainers": "涨幅榜", "losers": "跌幅榜", "volume": "成交量", "market_cap": "总市值", "hot": "热度榜", "arbitrage": "挂刀收益"}
            return {
                "msg_type": "interactive",
                "card": {
                    "header": {"title": {"tag": "plain_text", "content": f"📊 {filter_labels.get(filter_type, '排行')} TOP 8"}, "template": "blue"},
                    "elements": [
                        {"tag": "div", "text": {"tag": "lark_md", "content": "\n".join(lines)}},
                        {"tag": "hr"},
                        {"tag": "note", "elements": [{"tag": "plain_text", "content": "发送 /rank 涨幅|跌幅|成交|市值|热度|挂刀 切换"}]}
                    ]
                }
            }
        except Exception as e:
            return self._error_card(f"获取排行失败: {str(e)}")

    async def _cmd_market(self) -> dict:
        """市场概览"""
        try:
            overview = await market_service.get_overview()
            idx = overview.get("index", {}) or {}
            return {
                "msg_type": "interactive",
                "card": {
                    "header": {"title": {"tag": "plain_text", "content": "📈 市场概览"}, "template": "blue"},
                    "elements": [
                        {"tag": "div", "text": {"tag": "lark_md", "content": (
                            f"**饰品指数**: {idx.get('index_value', 'N/A')}\n"
                            f"**涨跌幅**: {idx.get('index_change_pct', 'N/A')}%\n"
                            f"**在线玩家**: {idx.get('online_players', 'N/A')}\n"
                            f"**24h成交量**: {overview.get('volume_24h', 'N/A')}"
                        )}},
                        {"tag": "hr"},
                        {"tag": "note", "elements": [{"tag": "plain_text", "content": "数据来源: CSQAQ | 发送 /help 查看更多命令"}]}
                    ]
                }
            }
        except Exception as e:
            return self._error_card(f"获取市场数据失败: {str(e)}")

    async def _cmd_portfolio(self, db: AsyncSession) -> dict:
        """持仓概览"""
        try:
            summary = await portfolio_service.get_summary(db)
            holdings = await portfolio_service.get_all(db)

            lines = [f"📦 持仓数: {summary.get('holding_count', 0)} 件",
                     f"💰 总成本: ¥{summary.get('total_cost', 0):,.2f}",
                     f"📊 当前市值: ¥{summary.get('total_value', 0):,.2f}",
                     f"📈 盈亏: ¥{summary.get('total_pnl', 0):,.2f} ({summary.get('total_pnl_pct', 0)}%)",
                     f"", f"**持仓明细:**"]

            for h in holdings[:5]:
                pnl_str = f"+¥{h.get('pnl', 0):.2f}" if h.get('pnl', 0) >= 0 else f"-¥{abs(h.get('pnl', 0)):.2f}"
                lines.append(f"- {h.get('item_name') or h.get('market_hash_name', 'N/A')[:20]}: 现价 ¥{h.get('current_price', 0):.2f} | {pnl_str}")

            return {
                "msg_type": "interactive",
                "card": {
                    "header": {"title": {"tag": "plain_text", "content": "💼 我的持仓"}, "template": "turquoise"},
                    "elements": [
                        {"tag": "div", "text": {"tag": "lark_md", "content": "\n".join(lines)}},
                        {"tag": "hr"},
                        {"tag": "note", "elements": [{"tag": "plain_text", "content": "发送 /help 查看更多命令"}]}
                    ]
                }
            }
        except Exception as e:
            return self._error_card(f"获取持仓失败: {str(e)}")

    async def _cmd_alert(self, text: str) -> dict:
        """查看/设置价格提醒"""
        text = text.replace("/alert", "").replace("/a ", "").strip()
        return {
            "msg_type": "interactive",
            "card": {
                "header": {"title": {"tag": "plain_text", "content": "⏰ 价格提醒"}, "template": "orange"},
                "elements": [
                    {"tag": "div", "text": {"tag": "lark_md", "content": (
                        "**设置提醒**: 请在 Web 端操作\n"
                        "打开 http://localhost:5173/alerts\n\n"
                        "支持:\n"
                        "- 价格高于/低于阈值\n"
                        "- 涨幅/跌幅超过指定百分比"
                    )}},
                ]
            }
        }

    async def _cmd_ai(self, db: AsyncSession, message: str, user_name: str) -> dict:
        """AI 问答"""
        try:
            full_response = ""
            async for chunk in ai_service.chat(
                db=db, message=message, conversation_id=None,
                context_hints={"include_market": True, "include_portfolio": True}
            ):
                full_response += chunk

            # Truncate for card
            if len(full_response) > 2000:
                full_response = full_response[:2000] + "\n\n...(内容过长，请在 Web 端查看完整回复)"

            return {
                "msg_type": "interactive",
                "card": {
                    "header": {"title": {"tag": "plain_text", "content": "🤖 AI 分析"}, "template": "purple"},
                    "elements": [
                        {"tag": "div", "text": {"tag": "lark_md", "content": full_response}},
                        {"tag": "hr"},
                        {"tag": "note", "elements": [{"tag": "plain_text", "content": f"Powered by Claude | @{user_name}"}]}
                    ]
                }
            }
        except Exception as e:
            return self._error_card(f"AI 服务异常: {str(e)}")

    # ---- Help ----

    def _help_card(self) -> dict:
        return {
            "msg_type": "interactive",
            "card": {
                "header": {"title": {"tag": "plain_text", "content": "🤖 CSQAQ 助手 - 命令列表"}, "template": "indigo"},
                "elements": [
                    {"tag": "div", "text": {"tag": "lark_md", "content": (
                        "**📊 数据查询**\n"
                        "- `/price <饰品名>` 查询实时价格\n"
                        "- `/search <关键词>` 搜索饰品\n"
                        "- `/rank <类型>` 排行榜 (涨幅/跌幅/成交/市值/热度/挂刀)\n"
                        "- `/market` 市场概览\n\n"
                        "**💼 个人管理**\n"
                        "- `/portfolio` 查看持仓盈亏\n"
                        "- `/alert` 价格提醒设置\n\n"
                        "**🤖 AI 分析**\n"
                        "- 直接发送问题，AI 基于实时数据回答\n"
                        "- 例: \"AK-47红线最近走势怎么样\"\n"
                        "- 例: \"分析我的持仓风险\""
                    )}},
                    {"tag": "hr"},
                    {"tag": "note", "elements": [{"tag": "plain_text", "content": "数据来源: CSQAQ API | AI: Claude"}]}
                ]
            }
        }

    # ---- Helpers ----

    def _error_card(self, msg: str) -> dict:
        return {
            "msg_type": "interactive",
            "card": {
                "header": {"title": {"tag": "plain_text", "content": "❌ 出错了"}, "template": "red"},
                "elements": [{"tag": "div", "text": {"tag": "lark_md", "content": msg}}]
            }
        }

    def text_reply(self, content: str) -> dict:
        return {"msg_type": "text", "content": {"text": content}}


feishu_bot = FeishuBot()


# ============================================================
# Scheduled Push
# ============================================================

class FeishuPusher:

    async def push_message(self, content: str, msg_type: str = "text") -> bool:
        """Push a message to Feishu group via webhook."""
        if not settings.feishu_webhook_url:
            logger.warning("Feishu webhook URL not configured")
            return False

        try:
            async with httpx.AsyncClient() as client:
                if msg_type == "text":
                    body = {"msg_type": "text", "content": {"text": content}}
                else:
                    body = json.loads(content) if isinstance(content, str) else content

                resp = await client.post(settings.feishu_webhook_url, json=body, timeout=15)
                result = resp.json()
                if result.get("code") == 0:
                    logger.info("Feishu push success")
                    return True
                else:
                    logger.error(f"Feishu push failed: {result}")
                    return False
        except Exception as e:
            logger.error(f"Feishu push error: {e}")
            return False

    async def push_alert(self, alert_data: dict) -> bool:
        """Push a triggered price alert."""
        content = (
            f"🚨 **价格提醒触发**\n"
            f"饰品: {alert_data.get('market_hash_name', 'N/A')}\n"
            f"类型: {alert_data.get('alert_type', 'N/A')}\n"
            f"阈值: ¥{alert_data.get('threshold_value', 0)}\n"
            f"当前价格: ¥{alert_data.get('current_price', 0)}\n"
            f"时间: {alert_data.get('triggered_at', '')}"
        )
        return await self.push_message(content)

    async def check_and_push_alerts(self, db: AsyncSession) -> list:
        """Check triggered alerts and push to Feishu."""
        triggered = await alert_service.check_alerts(db)
        for alert in triggered:
            await self.push_alert(alert)
        return triggered


feishu_pusher = FeishuPusher()
