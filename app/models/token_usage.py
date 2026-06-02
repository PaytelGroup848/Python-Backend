
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime
)

from app.db.database import Base


class TokenUsage(Base):

    __tablename__ = "token_usage"

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

    provider = Column(
        String,
        nullable=False
    )

    model = Column(
        String,
        nullable=False
    )

    prompt_tokens = Column(
        Integer,
        default=0
    )

    completion_tokens = Column(
        Integer,
        default=0
    )

    total_tokens = Column(
        Integer,
        default=0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )