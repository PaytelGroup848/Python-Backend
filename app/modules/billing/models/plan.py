from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Boolean,
    DateTime,
    Text
)

from datetime import datetime

from app.db.database import Base


class Plan(Base):

    __tablename__ = "plans"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    plan_code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    plan_name = Column(
        String(100),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    is_public = Column(
        Boolean,
        default=True,
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

    