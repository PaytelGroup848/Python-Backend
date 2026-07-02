from datetime import datetime
from enum import Enum

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,

    UniqueConstraint,
    func
)

from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from app.db.database import Base


class MessageRole(str, Enum):

    SYSTEM = "system"

    USER = "user"

    ASSISTANT = "assistant"

    TOOL = "tool"


class MessageStatus(str, Enum):

    PENDING = "pending"

    STREAMING = "streaming"

    COMPLETED = "completed"

    FAILED = "failed"


class ChatMessage(Base):

    __tablename__ = "chat_messages"

    __table_args__ = (
        UniqueConstraint(
            "conversation_id",
            "sequence_number",
            name="uq_chat_message_sequence"
        ),

        Index(
            "idx_chat_message_conversation",
            "conversation_id",
            "sequence_number"
        ),

        Index(
            "idx_chat_message_workspace",
            "workspace_id"
        ),

        Index(
            "idx_chat_message_org",
            "organization_id"
        ),

        Index(
            "idx_chat_message_created",
            "created_at"
        ),

    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True
    )

    organization_id: Mapped[int] = mapped_column(
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    workspace_id: Mapped[int] = mapped_column(
        ForeignKey(
            "workspaces.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey(
            "conversations.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    parent_message_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "chat_messages.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    role: Mapped[MessageRole] = mapped_column(
        SqlEnum(MessageRole),
        nullable=False
    )

    status: Mapped[MessageStatus] = mapped_column(
        SqlEnum(MessageStatus),
        nullable=False,
        default=MessageStatus.PENDING,
        server_default=MessageStatus.PENDING.value
    )

    sequence_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    model_release_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "model_releases.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    provider_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    input_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )

    output_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )

    latency_ms: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )

    finish_reason: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    metadata_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages",
        lazy="selectin"
    )