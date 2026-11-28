# app/models/assistant.py

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.database import Base


class Assistant(Base):

    __tablename__ = "assistants"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    code = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    description = Column(
        Text,
        nullable=True
    )

    system_prompt = Column(
        Text,
        nullable=True
    )

    owner_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", name="fk_assistants_owner_user_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    is_custom: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
        nullable=False,
    )

    share_slug: Mapped[Optional[str]] = mapped_column(
        String(64),
        unique=True,
        nullable=True,
        index=True,
    )

    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
        nullable=False,
    )

    strict_rag: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
        nullable=False,
    )

    allowed_domains: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        nullable=True,
    )

    welcome_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    config = relationship(

        "AssistantConfig",

        uselist=False,

        backref="assistant",

        lazy="selectin",

        cascade="all, delete-orphan",

    )