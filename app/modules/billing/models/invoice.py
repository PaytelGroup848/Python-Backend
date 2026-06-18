from datetime import datetime
from sqlalchemy import JSON

from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    Boolean,
    JSON
)

from app.db.database import Base


class Invoice(Base):

    __tablename__ = "invoices"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    subscription_id = Column(
        Integer,
        ForeignKey("subscriptions.id"),
        nullable=True
    )

    invoice_number = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    invoice_type = Column(
        String(50),
        default="subscription",
        nullable=False
    )

    subtotal = Column(
        Numeric(18, 6),
        default=0,
        nullable=False
    )

    tax_amount = Column(
        Numeric(18, 6),
        default=0,
        nullable=False
    )

    amount = Column(
        Numeric(18, 6),
        nullable=False
    )

    currency = Column(
        String(10),
        default="USD",
        nullable=False
    )

    currency_symbol = Column(
        String(10),
        nullable=True
    )

    status = Column(
        String(20),
        default="pending",
        nullable=False
    )

    billing_month = Column(
        String(7),
        nullable=False,
        index=True
    )


    period_start = Column(
        DateTime,
        nullable=True
    )

    period_end = Column(
        DateTime,
        nullable=True
    )

    payment_provider = Column(
        String(50),
        nullable=True
    )

    payment_reference = Column(
        String(255),
        nullable=True
    )

    external_reference = Column(
        String(255),
        nullable=True
    )

    auto_renew = Column(
        Boolean,
        default=False,
        nullable=False
    )

    due_date = Column(
        DateTime,
        nullable=True
    )

    paid_at = Column(
        DateTime,
        nullable=True
    )

    invoice_metadata = Column(
        JSON,
        nullable=True
    )

    notes = Column(
        String(500),
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    generated_at = Column(
        DateTime,
        default=datetime.utcnow,
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