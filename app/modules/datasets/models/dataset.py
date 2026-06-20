from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime
)

from app.db.database import Base


class Dataset(Base):

    __tablename__ = "datasets"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    domain = Column(
        String(100),
        nullable=False,
        index=True
    )

    version = Column(
        String(50),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    source = Column(
        String(255),
        nullable=True
    )

    record_count = Column(
        Integer,
        default=0,
        nullable=False
    )

    status = Column(
        String(50),
        default="draft",
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