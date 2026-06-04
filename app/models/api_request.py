from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    BigInteger,
    DateTime,
    ForeignKey
)

from app.db.database import Base


class ApiRequest(Base):

    __tablename__ = "api_requests"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    request_id = Column(
        String,
        nullable=False,
        unique=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    api_key_id = Column(
        Integer,
        ForeignKey("api_keys.id"),
        nullable=True
    )

    model_name = Column(
        String,
        nullable=False
    )

    provider = Column(
        String,
        nullable=False
    )

    prompt_tokens = Column(
        BigInteger,
        default=0
    )

    completion_tokens = Column(
        BigInteger,
        default=0
    )

    total_tokens = Column(
        BigInteger,
        default=0
    )

    latency_ms = Column(
        Integer,
        default=0
    )

    status_code = Column(
        Integer,
        default=200
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )