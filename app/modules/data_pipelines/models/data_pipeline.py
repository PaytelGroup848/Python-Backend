from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint
)

from app.db.database import Base


class DataPipeline(Base):

    __tablename__ = "data_pipelines"

    __table_args__ = (

        UniqueConstraint(

            "corpus_id",

            "version",

            name="uq_pipeline_corpus_version"
        ),
    )

    id = Column(
        Integer,
        primary_key=True
    )

    corpus_id = Column(
        Integer,
        ForeignKey(
            "corpora.id",
            name="fk_pipeline_corpus_id"
        ),
        nullable=False,
        index=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    pipeline_code = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True
    )

    dataset_id = Column(
        Integer,
        ForeignKey(
            "datasets.id",
            name="fk_pipeline_dataset_id"
        ),
        nullable=True,
        index=True
    )



    version = Column(
        String(100),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False,
        index=True
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