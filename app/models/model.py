from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime
)

from app.db.database import Base


class ModelRegistry(Base):

    __tablename__ = "models"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    model_name = Column(
        String,
        unique=True,
        nullable=False
    )

    provider = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )