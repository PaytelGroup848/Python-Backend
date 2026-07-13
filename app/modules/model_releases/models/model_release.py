from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    func
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

    model_version_id = Column(
        Integer,
        ForeignKey(
            "model_versions.id",
            name="fk_model_release_model_version_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
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

    checksum = Column(
        String(255),
        nullable=True
    )

    release_status = Column(
        String(50),
        nullable=False,
        default="DRAFT",
        server_default="DRAFT",
        index=True
    )

    is_default = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false"
    )

    created_by = Column(
        String(255),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        server_default=func.now(),
        onupdate=datetime.utcnow,
        nullable=False
    )