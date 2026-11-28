from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    BigInteger
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class KnowledgeBaseDocument(Base):

    __tablename__ = "knowledge_base_documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    knowledge_base_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "knowledge_bases.id",
            name="fk_kbd_knowledge_base_id"
        ),
        nullable=False,
        index=True
    )

    file_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    file_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )

    mime_type: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    file_size: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending"
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True
    )