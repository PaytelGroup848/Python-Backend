from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

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

    dataset_version_id = Column(
        Integer,
        ForeignKey(
            "dataset_versions.id",
            name="fk_evaluation_job_dataset_version_id",
        ),
        nullable=False,
        index=True,
    )

   

    runtime_configuration = Column(
        JSONB,
        nullable=False,
        default=dict,
    )

    metrics = Column(
        JSONB,
        nullable=False,
        default=dict,
    )

    summary = Column(
        JSONB,
        nullable=False,
        default=dict,
    )

    started_at = Column(
        DateTime,
        nullable=True,
    )

    completed_at = Column(
        DateTime,
        nullable=True,
    )

    duration_ms = Column(
        Float,
        nullable=True,
    )

    status = Column(
        String(50),
        default="pending",
        nullable=False
    )

    failure_reason = Column(
        String(1000),
        nullable=True,
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