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


class AssistantModelVersion(Base):

    __tablename__ = "assistant_model_versions"

    __table_args__ = (

        UniqueConstraint(
            "assistant_id",
            "model_version_id",
            name="uq_assistant_model_version"
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
            name="fk_amv_assistant_id"
        ),
        nullable=False,
        index=True
    )

    model_version_id = Column(
        Integer,
        ForeignKey(
            "model_versions.id",
            name="fk_amv_model_version_id"
        ),
        nullable=False,
        index=True
    )

    is_default = Column(
        Boolean,
        default=False,
        nullable=False
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