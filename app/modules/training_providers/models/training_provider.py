from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    JSON,
    func
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

    runtime_version = Column(
        String(100),
        nullable=True
    )

    provider_type = Column(
        String(100),
        nullable=False,
        index=True
    )

    runtime_class = Column(
        String(500),
        nullable=False
    )

    capabilities = Column(
        JSON,
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False
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