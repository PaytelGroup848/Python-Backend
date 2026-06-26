from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint
)

from app.db.database import Base
from sqlalchemy.dialects.postgresql import JSONB


class DatasetRecord(Base):

    __tablename__ = "dataset_records"

    __table_args__ = (

        UniqueConstraint(

            "dataset_id",

            "record_hash",

            name="uq_dataset_record_hash"
        ),
    )

    id = Column(
        Integer,
        primary_key=True
    )

    dataset_id = Column(
        Integer,
        ForeignKey(
            "datasets.id",
            name="fk_dataset_record_dataset_id"
        ),
        nullable=False,
        index=True
    )

    corpus_source_id = Column(
        Integer,
        ForeignKey(
            "corpus_sources.id",
            name="fk_dataset_record_corpus_source_id"
        ),
        nullable=True,
        index=True
    )



    record_type = Column(
        String(100),
        nullable=False,
        index=True
    )

    status = Column(
        String(50),
        nullable=False,
        index=True
    )

    record_hash = Column(
        String(255),
        nullable=False,
        index=True
    )

    validation_score = Column(
        Integer,
        nullable=True
    )

    input_text = Column(
        Text,
        nullable=False
    )

    output_text = Column(
        Text,
        nullable=True
    )

    metadata_json = Column(
        JSONB,
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