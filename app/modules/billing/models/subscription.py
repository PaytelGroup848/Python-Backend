from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    BigInteger,
    DateTime,
    Boolean,
    ForeignKey
)

from app.db.database import Base


class Subscription(Base):

    __tablename__ = "subscriptions"

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

    plan_id = Column(
        BigInteger,
        ForeignKey("plans.id"),
        nullable=True
    )

    plan_version_id = Column(
        BigInteger,
        ForeignKey("plan_versions.id"),
        nullable=True
    )

    plan_name = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        default="active",
        nullable=False
    )

    monthly_token_limit = Column(
        BigInteger,
        default=0
    )

    auto_renew = Column(
        Boolean,
        default=False
    )

    start_date = Column(
        DateTime,
        default=datetime.utcnow
    )

    end_date = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )