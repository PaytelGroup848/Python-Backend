from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
    func
)

from app.db.database import Base


class ModelPromotion(Base):

    __tablename__ = "model_promotions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    evaluation_job_id = Column(
        Integer,
        ForeignKey(
            "evaluation_jobs.id",
            name="fk_model_promotion_evaluation_job_id"
        ),
        nullable=False,
        index=True
    )

    promotion_status = Column(
        String(50),
        nullable=False,
        default="PENDING",
        server_default="PENDING",
        index=True
    )

    target_environment = Column(
        String(50),
        nullable=False,
        default="DEVELOPMENT",
        server_default="DEVELOPMENT"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true"
    )

    approved_by = Column(
        String(255),
        nullable=True
    )

    approved_at = Column(
        DateTime,
        nullable=True
    )

    approval_reason = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        server_default=func.now(),
        onupdate=datetime.utcnow,
        nullable=False
    )