from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class MiniAILead(Base):
    __tablename__ = "mini_ai_leads"
    __table_args__ = (
        Index("ix_mini_ai_leads_assistant_created", "assistant_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    assistant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("assistants.id", name="fk_mini_ai_leads_assistant_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    owner_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", name="fk_mini_ai_leads_owner_user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    visitor_name: Mapped[str] = mapped_column(String(120), nullable=False)
    visitor_contact: Mapped[str] = mapped_column(String(160), nullable=False)
    first_question: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


class MiniAIGap(Base):
    __tablename__ = "mini_ai_gaps"
    __table_args__ = (
        Index("ix_mini_ai_gaps_assistant_resolved", "assistant_id", "resolved"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    assistant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("assistants.id", name="fk_mini_ai_gaps_assistant_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_question: Mapped[str] = mapped_column(Text, nullable=False)
    hit_count: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default=text("1"),
        nullable=False,
    )
    resolved: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
