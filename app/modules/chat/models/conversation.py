from datetime import datetime
from enum import Enum

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    String,
    func,
    Index
)

from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from app.db.database import Base


class ConversationStatus(str, Enum):

    ACTIVE = "active"

    ARCHIVED = "archived"

    DELETED = "deleted"


class Conversation(Base):

    __tablename__ = "conversations"

    __table_args__ = (

        Index(
            "idx_conversation_org_workspace",
            "organization_id",
            "workspace_id"
        ),

        Index(
            "idx_conversation_user",
            "created_by"
        ),

        Index(
            "idx_conversation_last_message",
            "last_message_at"
        ),

        Index(
            "idx_conversation_status",
            "status"
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

    assistant_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "workspace_assistants.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    created_by: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id"
        ),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    status: Mapped[ConversationStatus] = mapped_column(
        SqlEnum(ConversationStatus),
        nullable=False,
        default=ConversationStatus.ACTIVE,
        server_default=ConversationStatus.ACTIVE.value
    )

    message_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )

    last_message_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True
    )

    last_message_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    pinned: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false"
    )

    archived: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false"
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

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    messages = relationship(
        "ChatMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy="selectin"
    )