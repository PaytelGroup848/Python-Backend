from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)

from sqlalchemy.dialects.postgresql import (
    JSONB
)

from app.db.database import Base


class PipelineExecutionArtifact(Base):

    __tablename__ = (
        "pipeline_execution_artifacts"
    )

    __table_args__ = (

        UniqueConstraint(
            "pipeline_run_id",
            "artifact_code",
            name=(
                "uq_pipeline_execution_"
                "artifact_code"
            ),
        ),

    )

    id = Column(
        BigInteger,
        primary_key=True,
    )

    pipeline_run_id = Column(
        Integer,
        ForeignKey(
            "pipeline_runs.id",
            name=(
                "fk_pipeline_execution_"
                "artifact_run_id"
            ),
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    producer_step_run_id = Column(
        Integer,
        ForeignKey(
            "pipeline_step_runs.id",
            name=(
                "fk_pipeline_execution_"
                "artifact_producer_step_run_id"
            ),
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    dataset_id = Column(
        Integer,
        ForeignKey(
            "datasets.id",
            name=(
                "fk_pipeline_execution_"
                "artifact_dataset_id"
            ),
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    corpus_source_id = Column(
        Integer,
        ForeignKey(
            "corpus_sources.id",
            name=(
                "fk_pipeline_execution_"
                "artifact_corpus_source_id"
            ),
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    artifact_code = Column(
        String(255),
        nullable=False,
        index=True,
    )

    artifact_type = Column(
        String(100),
        nullable=False,
        index=True,
    )

    storage_provider = Column(
        String(100),
        nullable=False,
        index=True,
    )

    storage_reference = Column(
        String(2000),
        nullable=False,
    )

    storage_instance_id = Column(
        Integer,
        ForeignKey(
            "storage_instances.id",
            name=(
                "fk_pipeline_execution_artifact_"
                "storage_instance_id"
            ),
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    mime_type = Column(
        String(255),
        nullable=True,
    )

    size_bytes = Column(
        BigInteger,
        nullable=True,
    )

    checksum = Column(
        String(255),
        nullable=True,
        index=True,
    )

    status = Column(
        String(50),
        nullable=False,
        index=True,
    )

    metadata_json = Column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
        onupdate=datetime.utcnow,
    )