from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    Float,
    DateTime,
    ForeignKey
)

from app.db.database import Base


class AssistantConfig(Base):

    __tablename__ = "assistant_configs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    assistant_id = Column(
        Integer,
        ForeignKey(
            "assistants.id",
            name="fk_assistant_config_assistant_id"
        ),
        nullable=False,
        unique=True,
        index=True
    )

    model_id = Column(
        Integer,
        ForeignKey(
            "models.id",
            name="fk_assistant_config_model_id"
        ),
        nullable=True,
        index=True
    )

    temperature = Column(
        Float,
        nullable=False,
        default=0.2
    )

    top_p = Column(
        Float,
        nullable=False,
        default=0.95
    )

    max_tokens = Column(
        Integer,
        nullable=False,
        default=4000
    )

    context_window = Column(
        Integer,
        nullable=False,
        default=8000
    )

    memory_enabled = Column(
        Boolean,
        nullable=False,
        default=True
    )

    rag_enabled = Column(
        Boolean,
        nullable=False,
        default=True
    )

    cag_enabled = Column(
        Boolean,
        nullable=False,
        default=False
    )

    tool_calling_enabled = Column(
        Boolean,
        nullable=False,
        default=False
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