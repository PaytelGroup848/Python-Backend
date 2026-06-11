from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Numeric,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint
)

from sqlalchemy.orm import (
    relationship
)

from datetime import datetime

from app.db.database import Base


class PlanPrice(Base):

    __tablename__ = "plan_prices"

    __table_args__ = (
        UniqueConstraint(
            "plan_version_id",
            "provider",
            "currency",
            "billing_cycle",
            name="uq_plan_price"
        ),
    )

    id = Column(
        BigInteger,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    plan_version_id = Column(
        BigInteger,
        ForeignKey(
            "plan_versions.id"
        ),
        nullable=False,
        index=True
    )

    provider = Column(
        String(50),
        nullable=False
    )

    external_price_id = Column(
        String(255),
        nullable=True
    )

    currency = Column(
        String(10),
        nullable=False
    )

    amount = Column(
        Numeric(
            18,
            6
        ),
        nullable=False
    )

    billing_cycle = Column(
        String(20),
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

    plan_version = relationship(
        "PlanVersion"
    )