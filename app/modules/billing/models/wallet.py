from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
    String
)

from app.db.database import Base


class Wallet(Base):

    __tablename__ = "wallets"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    balance = Column(
        Numeric(18, 6),
        default=0,
        nullable=False
    )

    currency = Column(
        String(10),
        default="USD",
        nullable=False
    )

    status = Column(
        String(20),
        default="active",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )