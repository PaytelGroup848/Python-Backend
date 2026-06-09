from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    BigInteger,
    DateTime
)

from app.db.database import Base


class UsageLimit(Base):

    __tablename__ = "usage_limits"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    plan_name = Column(
        String,
        unique=True,
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
        Integer,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )