from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    String,
    Text,
    DateTime,
    ForeignKey
)

from app.db.database import Base


class WalletTransaction(Base):

    __tablename__ = "wallet_transactions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    wallet_id = Column(
        Integer,
        ForeignKey("wallets.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    transaction_type = Column(
        String(50),
        nullable=False
    )

    status = Column(
        String(20),
        default="completed",
        nullable=False
    )

    amount = Column(
        Numeric(18, 6),
        nullable=False
    )

    balance_before = Column(
        Numeric(18, 6),
        nullable=False
    )

    balance_after = Column(
        Numeric(18, 6),
        nullable=False
    )

    reference_type = Column(
        String(50),
        nullable=True
    )

    reference_id = Column(
        String(255),
        nullable=True
    )

    description = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )