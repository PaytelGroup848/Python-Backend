from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime
)

from sqlalchemy.sql import func

from app.db.database import Base

from sqlalchemy import ForeignKey


class DocumentJob(Base):

    __tablename__ = "document_jobs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    filename = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        default="processing"
    )

    chunks_stored = Column(
        Integer,
        default=0
    )

    error_message = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    knowledge_base_document_id = Column(
        Integer,
        ForeignKey(
            "knowledge_base_documents.id",
            name="fk_document_jobs_kbd_id"
        ),
        nullable=False,
        index=True
    )