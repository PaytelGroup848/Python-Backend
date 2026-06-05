from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime
)

from app.db.database import Base


class ModelPricing(Base):

    __tablename__ = "model_pricing"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    model_name = Column(
        String,
        unique=True,
        nullable=False
    )

    provider = Column(
        String,
        nullable=False
    )

    input_cost_per_1k = Column(
        Float,
        nullable=False
    )

    output_cost_per_1k = Column(
        Float,
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )