from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)

from app.db.database import Base


class ModelRelease(Base):

    __tablename__ = "model_releases"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    promotion_id = Column(
        Integer,
        ForeignKey(
            "model_promotions.id",
            name="fk_model_release_promotion_id"
        ),
        nullable=False,
        index=True
    )

    release_version = Column(
        String(100),
        nullable=False
    )

    release_name = Column(
        String(255),
        nullable=False
    )

    release_notes = Column(
        Text,
        nullable=True
    )

    release_status = Column(
        String(50),
        nullable=False,
        default="draft"
    )

    created_by = Column(
        String(255),
        nullable=True
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