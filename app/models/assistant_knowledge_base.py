from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint
)

from app.db.database import Base
from sqlalchemy import Index


class AssistantKnowledgeBase(Base):

    __tablename__ = "assistant_knowledge_bases"

    __table_args__ = (

        UniqueConstraint(
            "assistant_id",
            "knowledge_base_id",
            name="uq_assistant_knowledge_base"
        ),

        Index(
            "ix_akb_assistant_kb",
            "assistant_id",
            "knowledge_base_id"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    assistant_id = Column(
        Integer,
        ForeignKey(
            "assistants.id",
            name="fk_akb_assistant_id"
        ),
        nullable=False,
        index=True
    )

    knowledge_base_id = Column(
        Integer,
        ForeignKey(
            "knowledge_bases.id",
            name="fk_akb_knowledge_base_id"
        ),
        nullable=False,
        index=True
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