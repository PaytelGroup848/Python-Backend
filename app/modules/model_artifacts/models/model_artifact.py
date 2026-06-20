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


class ModelArtifact(Base):

    __tablename__ = "model_artifacts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    training_job_id = Column(
        Integer,
        ForeignKey(
            "training_jobs.id",
            name="fk_model_artifact_training_job_id"
        ),
        nullable=False,
        index=True
    )

    artifact_name = Column(
        String(255),
        nullable=False
    )

    artifact_path = Column(
        String(1000),
        nullable=False
    )

    artifact_type = Column(
        String(100),
        nullable=False
    )

    size_bytes = Column(
        BigInteger,
        nullable=True
    )

    checksum = Column(
        String(255),
        nullable=True
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