from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    BigInteger,
    DateTime,
    ForeignKey,
    func
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

    artifact_version = Column(
        Integer,
        nullable=False,
        default=1
    )

    storage_provider = Column(
        String(50),
        nullable=False,
        default="LOCAL"
    )

    mime_type = Column(
        String(255),
        nullable=True
    )

    compression = Column(
        String(50),
        nullable=True
    )

    status = Column(
        String(50),
        nullable=False,
        default="READY"
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