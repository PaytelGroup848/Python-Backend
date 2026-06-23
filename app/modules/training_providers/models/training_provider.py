from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime
)

from app.db.database import Base


class TrainingProvider(Base):

    __tablename__ = "training_providers"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    code = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    display_name = Column(
        String(255),
        nullable=False
    )

    provider_type = Column(
        String(100),
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