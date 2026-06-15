from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    JSON
)

from app.db.database import Base


class Payment(Base):

    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    payment_reference = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    invoice_id = Column(
        Integer,
        ForeignKey("invoices.id"),
        nullable=True
    )

    subscription_id = Column(
        Integer,
        ForeignKey("subscriptions.id"),
        nullable=True
    )

    provider = Column(
        String(50),
        nullable=False
    )

    payment_type = Column(
        String(50),
        nullable=False
    )

    payment_method = Column(
        String(100),
        nullable=True
    )

    amount = Column(
        Numeric(18, 6),
        nullable=False
    )

    currency = Column(
        String(10),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False
    )

    failure_reason = Column(
        String(500),
        nullable=True
    )

    gateway_order_id = Column(
        String(255),
        nullable=True
    )



    gateway_payment_id = Column(
        String(255),
        nullable=True
    )

    idempotency_key = Column(
        String(255),
        unique=True,
        nullable=True,
        index=True
    )

    payment_metadata = Column(
        JSON,
        nullable=True
    )

    processed_at = Column(
        DateTime,
        nullable=True
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