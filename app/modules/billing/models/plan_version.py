from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
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


class PlanVersion(Base):

    __tablename__ = "plan_versions"

    __table_args__ = (
        UniqueConstraint(
            "plan_id",
            "version_number",
            name="uq_plan_version"
        ),
    )

    id = Column(
        BigInteger,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    plan_id = Column(
        BigInteger,
        ForeignKey("plans.id"),
        nullable=False,
        index=True
    )

    version_number = Column(
        Integer,
        nullable=False
    )

    monthly_token_limit = Column(
        BigInteger,
        nullable=False
    )

    monthly_request_limit = Column(
        BigInteger,
        nullable=False
    )

    monthly_cost_limit = Column(
        BigInteger,
        nullable=True
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

    plan = relationship(
        "Plan"
    )