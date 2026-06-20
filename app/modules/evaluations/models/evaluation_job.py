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


class EvaluationJob(Base):

    __tablename__ = "evaluation_jobs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    artifact_id = Column(
        Integer,
        ForeignKey(
            "model_artifacts.id",
            name="fk_evaluation_job_artifact_id"
        ),
        nullable=False,
        index=True
    )

    evaluation_type = Column(
        String(100),
        nullable=False
    )

    accuracy_score = Column(
        Float,
        nullable=True
    )

    hallucination_score = Column(
        Float,
        nullable=True
    )

    latency_score = Column(
        Float,
        nullable=True
    )

    overall_score = Column(
        Float,
        nullable=True
    )

    status = Column(
        String(50),
        default="pending",
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