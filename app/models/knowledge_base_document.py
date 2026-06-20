from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    BigInteger
)

from app.db.database import Base


class KnowledgeBaseDocument(Base):

    __tablename__ = "knowledge_base_documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    knowledge_base_id = Column(
        Integer,
        ForeignKey(
            "knowledge_bases.id",
            name="fk_kbd_knowledge_base_id"
        ),
        nullable=False,
        index=True
    )

    file_name = Column(
        String(500),
        nullable=False
    )

    file_path = Column(
        String(1000),
        nullable=False
    )

    mime_type = Column(
        String(255),
        nullable=True
    )

    file_size = Column(
        BigInteger,
        nullable=True
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

    status = Column(
        String(50),
        nullable=False,
        default="pending"
    )

    error_message = Column(
        String,
        nullable=True
    )