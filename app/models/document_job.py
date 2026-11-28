from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.database import Base


class DocumentJob(Base):

    __tablename__ = "document_jobs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    filename: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    status: Mapped[Optional[str]] = mapped_column(
        String,
        default="processing"
    )

    chunks_stored: Mapped[Optional[int]] = mapped_column(
        Integer,
        default=0
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True
    )

    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    knowledge_base_document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "knowledge_base_documents.id",
            name="fk_document_jobs_kbd_id"
        ),
        nullable=False,
        index=True
    )