from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

from app.db.database import Base


class IngestionJob(Base):

    __tablename__ = "ingestion_jobs"

    

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    corpus_source_id = Column(
        Integer,
        ForeignKey(
            "corpus_sources.id",
            name="fk_ingestion_job_corpus_source_id"
        ),
        nullable=False,
        index=True
    )

    dataset_id = Column(
        Integer,
        ForeignKey(
            "datasets.id",
            name="fk_ingestion_job_dataset_id"
        ),
        nullable=True,
        index=True
    )

    status = Column(
        String(50),
        nullable=False,
        index=True
    )

    records_processed = Column(
        Integer,
        nullable=False
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

    completed_at = Column(
        DateTime,
        nullable=True
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )