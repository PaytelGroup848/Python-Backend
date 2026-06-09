from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey
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

    invoice_number = Column(
        String,
        unique=True,
        nullable=False
    )

    amount = Column(
        Float,
        nullable=False
    )

    currency = Column(
        String,
        default="USD"
    )

    status = Column(
        String,
        default="pending"
    )

    billing_month = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )