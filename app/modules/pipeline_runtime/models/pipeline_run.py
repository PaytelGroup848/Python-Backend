from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

from app.db.database import Base
from sqlalchemy.dialects.postgresql import JSONB


class PipelineRun(Base):

    __tablename__ = "pipeline_runs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    pipeline_id = Column(
        Integer,
        ForeignKey(
            "data_pipelines.id",
            name="fk_pipeline_run_pipeline_id"
        ),
        nullable=False,
        index=True
    )

    dataset_id = Column(
        Integer,
        ForeignKey(
            "datasets.id",
            name="fk_pipeline_run_dataset_id"
        ),
        nullable=True,
        index=True
    )

    corpus_source_id = Column(
        Integer,
        ForeignKey(
            "corpus_sources.id",
            name="fk_pipeline_run_corpus_source_id"
        ),
        nullable=True,
        index=True
    )

    run_code = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True
    )


    trigger_type = Column(
        String(100),
        nullable=False,
        index=True
    )

    status = Column(
        String(50),
        nullable=False,
        index=True
    )

    metrics_json = Column(
        JSONB,
        nullable=True
    )

    started_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )

    error_message = Column(
        String,
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