import sqlalchemy as sa

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String
)

from app.db.database import Base


class ModelRegistry(Base):

    __tablename__ = "models"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    provider_id = Column(
        Integer,
        ForeignKey("providers.id"),
        nullable=False,
        index=True
    )

    code = Column(
        String(100),
        unique=True,
        nullable=False
    )

    display_name = Column(
        String(255),
        nullable=False
    )

    description = Column(
        String,
        nullable=True
    )


    status = Column(
        String(50),
        nullable=False,
        default="DRAFT",
        server_default="DRAFT",
        index=True
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=sa.func.now(),
        onupdate=datetime.utcnow
    )