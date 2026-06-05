"""AI conversation and message models."""
from datetime import datetime
from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(256), default="New Conversation")
    created_at: Mapped[str] = mapped_column(String(32), default=lambda: datetime.now().isoformat())
    updated_at: Mapped[str] = mapped_column(String(32), default=lambda: datetime.now().isoformat())

    messages = relationship("AIMessage", back_populates="conversation", cascade="all, delete-orphan")


class AIMessage(Base):
    __tablename__ = "ai_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(Integer, ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    context_json: Mapped[str] = mapped_column(Text, nullable=True)  # JSON: injected context data
    token_count: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), default=lambda: datetime.now().isoformat())

    conversation = relationship("AIConversation", back_populates="messages")
