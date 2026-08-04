# app/models/assistant.py

from datetime import datetime


from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text
)

from sqlalchemy.orm import (
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