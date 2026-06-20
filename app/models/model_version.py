from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint
)

from app.db.database import Base


class ModelVersion(Base):

    __tablename__ = "model_versions"

    __table_args__ = (

        UniqueConstraint(

            "model_id",

            "version",

            name="uq_model_versions_model_version"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    model_id = Column(
        Integer,
        ForeignKey("models.id"),
        nullable=False,
        index=True
    )

    version = Column(
        String(100),
        nullable=False,
        index=True
    )

    display_name = Column(
        String(255),
        nullable=False
    )

    description = Column(
        String,
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